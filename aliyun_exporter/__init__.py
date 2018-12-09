import argparse
import yaml
import logging
import signal
import sys
import time

from prometheus_client import start_http_server
from prometheus_client.core import REGISTRY

from aliyun_exporter.collector import AliyunCollector, CollectorConfig


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
    parser.add_argument('-p', '--port', default=9522,
                        help='exporter exposed port')
    args = parser.parse_args()

    with open(args.config_file, 'r') as config_file:
        cfg = yaml.load(config_file)
    collector_config = CollectorConfig(**cfg)

    collector = AliyunCollector(collector_config)
    REGISTRY.register(collector)

    logging.info("Start exporter, listen on {}".format(args.port))
    start_http_server(args.port)

    try:
        while True:
            time.sleep(5)
    except KeyboardInterrupt:
        pass

