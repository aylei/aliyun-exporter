import json

from aliyunsdkcore.client import AcsClient
from cachetools import cached, TTLCache
from prometheus_client.metrics_core import GaugeMetricFamily

import aliyunsdkecs.request.v20140526.DescribeInstancesRequest as DescribeECS
import aliyunsdkrds.request.v20140815.DescribeDBInstancesRequest as DescribeRDS
import aliyunsdkr_kvstore.request.v20150101.DescribeInstancesRequest as DescribeRedis
import aliyunsdkslb.request.v20140515.DescribeLoadBalancersRequest as DescribeSLB
import aliyunsdkdds.request.v20151201.DescribeDBInstancesRequest as Mongodb

from aliyun_exporter.utils import try_or_else

cache = TTLCache(maxsize=100, ttl=3600)

'''
InfoProvider provides the information of cloud resources as metric.

The result from alibaba cloud API will be cached for an hour. 

Different resources should implement its own 'xxx_info' function. 

Different resource has different information structure, and most of
them are nested, for simplicity, we map the top-level attributes to the
labels of metric, and handle nested attribute specially. If a nested
attribute is not handled explicitly, it will be dropped.
'''
class InfoProvider():

    def __init__(self, client: AcsClient):
        self.client = client

    @cached(cache)
    def get_metrics(self, resource: str) -> GaugeMetricFamily:
        return {
            'ecs': lambda : self.ecs_info(),
            'rds': lambda : self.rds_info(),
            'redis': lambda : self.redis_info(),
            'slb':lambda : self.slb_info(),
            'mongodb':lambda : self.mongodb_info(),
        }[resource]()

    def ecs_info(self) -> GaugeMetricFamily:
        req = DescribeECS.DescribeInstancesRequest()
        nested_handler = {
            'InnerIpAddress': lambda obj : try_or_else(lambda : obj['IpAddress'][0], ''),
            'PublicIpAddress': lambda obj : try_or_else(lambda : obj['IpAddress'][0], ''),
            'VpcAttributes': lambda obj : try_or_else(lambda : obj['PrivateIpAddress']['IpAddress'][0], ''),
        }
        return self.info_template(req, 'aliyun_meta_ecs_info', nested_handler=nested_handler)

    def rds_info(self) -> GaugeMetricFamily:
        req = DescribeRDS.DescribeDBInstancesRequest()
        return self.info_template(req, 'aliyun_meta_rds_info', to_list=lambda data: data['Items']['DBInstance'])

    def redis_info(self) -> GaugeMetricFamily:
        req = DescribeRedis.DescribeInstancesRequest()
        return self.info_template(req, 'aliyun_meta_redis_info', to_list=lambda data: data['Instances']['KVStoreInstance'])

    def slb_info(self) -> GaugeMetricFamily:
        req = DescribeSLB.DescribeLoadBalancersRequest()
        return self.info_template(req, 'aliyun_meta_slb_info', to_list=lambda data: data['LoadBalancers']['LoadBalancer'])

    def mongodb_info(self) -> GaugeMetricFamily:
        req = Mongodb.DescribeDBInstancesRequest()
        return self.info_template(req, 'aliyun_meta_mongodb_info', to_list=lambda data: data['DBInstances']['DBInstance'])

    '''
    Template method to retrieve resource information and transform to metric.
    '''
    def info_template(self,
                      req,
                      name,
                      desc='',
                      page_size=100,
                      page_num=1,
                      nested_handler=None,
                      to_list=(lambda data: data['Instances']['Instance'])) -> GaugeMetricFamily:
        gauge = None
        label_keys = None
        for instance in self.pager_generator(req, page_size, page_num, to_list):
            if gauge is None:
                label_keys = self.label_keys(instance, nested_handler)
                gauge = GaugeMetricFamily(name, desc, labels=label_keys)
            gauge.add_metric(labels=self.label_values(instance, label_keys, nested_handler), value=1.0)
        return gauge

    def pager_generator(self, req, page_size, page_num, to_list):
        req.set_PageSize(page_size)
        while True:
            req.set_PageNumber(page_num)
            resp = self.client.do_action_with_exception(req)
            data = json.loads(resp)
            instances = to_list(data)
            for instance in instances:
                yield instance
            if len(instances) < page_size:
                break
            page_num += 1

    def label_keys(self, instance, nested_handler=None):
        if nested_handler is None:
            nested_handler = {}
        return [k for k, v in instance.items()
                if k in nested_handler or isinstance(v, str) or isinstance(v, int)]

    def label_values(self, instance, label_keys, nested_handler=None):
        if nested_handler is None:
            nested_handler = {}
        return map(lambda k: str(nested_handler[k](instance[k])) if k in nested_handler else try_or_else(lambda: str(instance[k]), ''),
                   label_keys)


