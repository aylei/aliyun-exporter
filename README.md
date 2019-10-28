# Prometheus Exporter for Alibaba Cloud

# Note: This repository has been archived due to lacking of human power.

![license](https://img.shields.io/hexpm/l/plug.svg)
[![help wanted](https://img.shields.io/github/issues/aylei/aliyun-exporter/help%20wanted.svg)](https://github.com/aylei/aliyun-exporter/issues?q=is%3Aissue+is%3Aopen+label%3A%22help+wanted%22)
[![pypi](https://img.shields.io/pypi/v/aliyun-exporter.svg)](https://pypi.org/project/aliyun-exporter/)
[![docker](https://img.shields.io/docker/pulls/aylei/aliyun-exporter.svg)](https://cloud.docker.com/u/aylei/repository/docker/aylei/aliyun-exporter)
[![Build Status](https://travis-ci.org/aylei/aliyun-exporter.svg?branch=master)](https://travis-ci.org/aylei/aliyun-exporter)

[中文](./README_cn.md)

* [Features](#features)
* [Screenshots](#screenshots)
* [Quick Start](#quick-start)
* [Installation](#installation)
* [Usage](#usage)
* [Docker Image](#docker-image)
* [Configuration](#configuration)
* [Metrics Meta](#metrics-meta)
* [Scale and HA Setup](#scale-and-ha-setup)
* [Contribute](#contribute)

This Prometheus exporter collects metrics from the [CloudMonitor API](https://partners-intl.aliyun.com/help/doc-detail/51939.htm) of Alibaba Cloud. It can help you:

* integrate CloudMonitor to your Monitoring System.
* leverage the power of PromQL, Alertmanager and Grafana(see [Screenshots](#)).
* analyze metrics however you want.
* save money. Api invocation is far cheaper than other services provided by CloudMonitor.

This project also provides an out-of-box solution for full-stack monitoring of Alibaba Cloud, including dashboards, alerting and diagnosing.

## Screenshots

![gif](/static/img/stack.gif)

[more screenshots here](./screenshots.md)

## Quick Start

A docker-compose stack is provided to launch the entire monitoring stack with Aliyun-Exporter, Prometheus, Grafana and Alertmanager.

Pre-requisites: docker 1.17+

```bash
git clone git@github.com:aylei/aliyun-exporter.git
cd docker-compose
ALIYUN_ACCESS_ID=YOUR_ACCESS_ID ALIYUN_ACCESS_SECRET=YOUR_ACCESS_KEY docker-compose up
```

Investigate dashboards in [localhost:3000](http://localhost:3000) (the default credential for Grafana is admin:admin).

For more details, see [Docker Compose](#docker-compose).

## Installation

Python 3.5+ is required.

```bash
pip3 install aliyun-exporter
```

## Usage

Config your credential and interested metrics:

```yaml
credential:
  access_key_id: <YOUR_ACCESS_KEY_ID>
  access_key_secret: <YOUR_ACCESS_KEY_SECRET>
  region_id: <REGION_ID>

metrics:
  acs_cdn:
  - name: QPS
  acs_mongodb:
  - name: CPUUtilization
    period: 300
```

Run the exporter:

```bash
> aliyun-exporter -p 9525 -c aliyun-exporter.yml
```

The default port is 9525, default config file location is `./aliyun-exporter.yml`.

Visit metrics in [localhost:9525/metrics](http://localhost:9525/metrics)

## Docker Image

Install
```bash
docker pull aylei/aliyun-exporter:0.3.1
```

To run the container, external configuration file is required:
```bash
docker run -p 9525:9525 -v $(pwd)/aliyun-exporter.yml:$(pwd)/aliyun-exporter.yml aylei/aliyun-exporter:0.3.1 -c $(pwd)/aliyun-exporter.yml
```

## Configuration

```yaml
rate_limit: 5 # request rate limit per second. default: 10
credential:
  access_key_id: <YOUR_ACCESS_KEY_ID> # required
  access_key_secret: <YOUR_ACCESS_KEY_SECRET> # required
  region_id: <REGION_ID> # default: 'cn-hangzhou'
  
metrics: # required, metrics specifications
  acs_cdn: # required, Project Name of CloudMonitor
  - name: QPS # required, Metric Name of CloudMonitor, belongs to a certain Project
    rename: qps # rename the related prometheus metric. default: same as the 'name'
    period: 60 # query period. default: 60
    measure: Average # measure field in the response. default: Average

info_metrics:
  - ecs
  - rds
  - redis
```

Notes:

* Find your target metrics using [Metrics Meta](#metrics-meta)
* CloudMonitor API has an rate limit, tuning the `rate_limit` configuration if the requests are rejected.
* CloudMonitor API also has an monthly quota for invocations (AFAIK, 5,000,000 invocations / month for free). Plan your usage in advance. 

> Given that you have 50 metrics to scrape with 60s scrape interval, about 2,160,000 requests will be sent by the exporter for 30 days.

## Special Project

Some metrics are not included in the Cloud Monitor API. For these metrics, we keep the configuration abstraction consistent by defining special projects.

Special Projects:

* `rds_performance`: RDS performance metrics, available metric names: [Performance parameter table](https://www.alibabacloud.com/help/doc-detail/26316.htm?spm=a2c63.p38356.b99.361.694917e6Rtuu9i)

> An example configuration file of special project is provided as `special-projects.yml`

**Note**: special projects invokes different API with ordinary metrics, so it will not consume your Cloud Monitor API invocation quota. But the API of special projects could be slow, so it is recommended to separate special projects into a standalone exporter instance.

## Metrics Meta

`aliyun-exporter` shipped with a simple site hosting the metrics meta from the CloudMonitor API. You can visit the metric meta in [localhost:9525](http://localhost:9525) after launching the exporter.

* `host:port` will host all the available monitor projects
* `host:port/projects/{project}` will host the metrics meta of a certain project
* `host:port/yaml/{project}` will host a config YAML of the project's metrics

you can easily navigate in this pages by hyperlink.

## Docker Compose

From `0.3.1`, we provide a docker-compose stack to help users building monitoring stack from scratch. The stack contains:

* aliyun-exporter (this project): Retrieving metrics (and instance information) from Alibaba Cloud.
* [Prometheus](https://github.com/prometheus/prometheus): Metric storage and alerting calculation.
* [Alertmanager](https://github.com/prometheus/alertmanager): Alert routing and notifying.
* [Grafana](https://github.com/grafana/grafana): Dashboards.
* [prometheus-webhook-dingtalk](https://github.com/timonwong/prometheus-webhook-dingtalk): DingTalk (a.k.a. DingDing) notification integrating.

Here's a detailed launch guide:

```bash
# config prometheus external host
export PROMETHEUS_HOST=YOUR_PUBLIC_IP_OR_HOSTNAME
# config dingtalk robot token
export DINGTALK_TOKEN=YOUR_DINGTALK_ROBOT_TOEKN
# config aliyun-exporter credential
export ALIYUN_REGION=YOUR_REGION
export ALIYUN_ACCESS_ID=YOUR_ID
export ALIYUN_ACCESS_SECRET=YOUR_SECRET
docker-compose up -d
```

After launching, you can access: 

* grafana: http://localhost:3000
* prometheus: http://localhost:9090
* alertmanager: http://localhost:9093

You may customize the configuration of this components by editing the configuration files in `./docker-compose/{component}`

## Telemetry

Request success summary and failure summary are exposed in `cloudmonitor_request_latency_seconds` and `cloudmonitor_failed_request_latency_seconds`.

Each `Project-Metric` pair will have a corresponding metric named `aliyun_{project}_{metric}_up`, which indicates whether this metric are successfully scraped.

## Scale and HA Setup

The CloudMonitor API could be slow if you have large amount of resources. You can separate metrics over multiple exporter instances to scale.

For HA setup, simply duplicate your deployments: 2 * prometheus, and 2 * exporter for each prometheus.

> HA Setup will double your requests, which may run out your quota.

## Contribute

Feel free to open issues and pull requests, any feedback will be highly appreciated!

Please check the [`help wanted`](https://github.com/aylei/aliyun-exporter/issues?q=is%3Aissue+is%3Aopen+label%3A%22help+wanted%22) label to find issues that are good for getting started.

Besides, contributing to new [alert rules](./docker-compose/prometheus/rules.yml), new [dashboards](./docker-compose/grafana/dashboards) is also welcomed!

