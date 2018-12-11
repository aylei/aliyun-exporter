import json
import logging
import time

from concurrent.futures import ThreadPoolExecutor
from prometheus_client import Summary
from prometheus_client.core import GaugeMetricFamily, REGISTRY
from aliyunsdkcore.client import AcsClient
from aliyunsdkcms.request.v20180308 import QueryMetricLastRequest
from ratelimiter import RateLimiter

requestSummary = Summary('cloudmonitor_request_latency_seconds', 'CloudMonitor request latency', ['project'])
requestFailedSummary = Summary('cloudmonitor_failed_request_latency_seconds', 'CloudMonitor failed request latency', ['project'])

class CollectorConfig(object):
    def __init__(self,
                 pool_size=10,
                 rate_limit=10,
                 credential=None,
                 metrics=None,
                 ):
        # if metrics is None:
        # raise Exception('Metrics config must be set.')
        if credential is None or \
                credential['access_key_id'] is None or \
                credential['access_key_secret'] is None:
            raise Exception('Credential is not fully configured.')
        self.credential = credential
        self.metrics = metrics
        self.rate_limit = rate_limit
        self.pool_size = pool_size


class AliyunCollector(object):
    def __init__(self, config: CollectorConfig):
        self.metrics = config.metrics
        self.client = AcsClient(
            ak=config.credential['access_key_id'],
            secret=config.credential['access_key_secret'],
            region_id=config.credential['region_id']
        )
        self.pool = ThreadPoolExecutor(max_workers=config.pool_size)
        self.rateLimiter = RateLimiter(max_calls=config.rate_limit)

    def query_metric(self, project: str, metric: str, period: int):
        with self.rateLimiter:
            req = QueryMetricLastRequest.QueryMetricLastRequest()
            req.set_Project(project)
            req.set_Metric(metric)
            req.set_Period(period)
            start_time = time.time()
            try:
                resp = self.client.do_action_with_exception(req)
            except Exception as e:
                logging.error('Error request cloud monitor api', e)
                requestFailedSummary.labels(project).observe(time.time() - start_time)
                return []
            else:
                requestSummary.labels(project).observe(time.time() - start_time)
        data = json.loads(resp)
        points = json.loads(data['Datapoints'])
        return points

    def parse_label_keys(self, point):
        return [k for k in point if k not in ['timestamp', 'Maximum', 'Minimum', 'Average']]


    def format_metric_name(self, project, name):
        return 'aliyun_{}_{}'.format(project, name)

    def metric_generator(self, project, metric):
        if 'name' not in metric:
            raise Exception('name must be set in metric item.')
        name = metric['name']
        metric_name = metric['name']
        period = 60
        measure = 'Average'
        if 'rename' in metric:
            name = metric['rename']
        if 'period' in metric:
            period = metric['period']
        if 'measures' in metric:
            measure = metric['measure']

        try:
            points = self.query_metric(project, metric_name, period)
        except Exception as e:
            logging.error('Error query metrics for {}_{}'.format(project, metric_name), e)
            yield metric_up_gauge(self.format_metric_name(project, name), False)
            return
        if len(points) < 1:
            yield metric_up_gauge(self.format_metric_name(project, name), False)
            return
        label_keys = self.parse_label_keys(points[0])
        gauge = GaugeMetricFamily(self.format_metric_name(project, name), '', labels=label_keys)
        for point in points:
            gauge.add_metric([point[k] for k in label_keys], point[measure])
        yield gauge
        yield metric_up_gauge(self.format_metric_name(project, name), True)

    def collect(self):
        for project in self.metrics:
            for metric in self.metrics[project]:
                yield from self.metric_generator(project, metric)


def metric_up_gauge(resource: str, succeeded=True):
    metric_name = resource + '_up'
    description = 'Did the {} fetch succeed.'.format(resource)
    return GaugeMetricFamily(metric_name, description, value=int(succeeded))