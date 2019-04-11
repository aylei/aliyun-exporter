import argparse
from wsgiref.simple_server import make_server

import yaml
import logging
import signal
import sys
import time

from prometheus_client.core import REGISTRY

from aliyun_exporter.collector import AliyunCollector, CollectorConfig
from aliyun_exporter.web import create_app


def shutdown():
    logging.info('Shutting down, see you next time!')
    sys.exit(1)

def signal_handler():
    shutdown()

def main():
    signal.signal(signal.SIGTERM, signal_handler)
    logging.getLogger().setLevel(logging.INFO)

    parser = argparse.ArgumentParser(description="Aliyun CloudMonitor exporter for Prometheus.")
    parser.add_argument('-c', '--config-file', default='aliyun-exporter.yml',
                       help='path to configuration file.')
    parser.add_argument('-p', '--port', default=9525,
                        help='exporter exposed port')
    args = parser.parse_args()

    with open(args.config_file, 'r') as config_file:
        cfg = yaml.load(config_file, Loader=yaml.FullLoader)
    collector_config = CollectorConfig(**cfg)

    collector = AliyunCollector(collector_config)
    REGISTRY.register(collector)

    app = create_app(collector_config)

    logging.info("Start exporter, listen on {}".format(int(args.port)))
    httpd = make_server('', int(args.port), app)
    httpd.serve_forever()

    try:
        while True:
            time.sleep(5)
    except KeyboardInterrupt:
        pass

