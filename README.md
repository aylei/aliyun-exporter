# Prometheus Exporter for Alibaba Cloud

![license](https://img.shields.io/hexpm/l/plug.svg)
![pypi](https://img.shields.io/pypi/v/aliyun-exporter.svg)
![docker](https://img.shields.io/docker/pulls/aylei/aliyun-exporter.svg)

[中文](#中文)

* [Screenshots](#screenshots)
* [Installation](#installation)
* [Usage](#usage)
* [Docker Image](#docker-image)
* [Configuration](#configuration)
* [Scale and HA Setup](#scale-and-ha-setup)
* [Contribute](#contribute)

This Prometheus exporter collects metrics from the [CloudMonitor API](https://help.aliyun.com/document_detail/51939.html?spm=a2c4g.11186623.2.17.51dd750eNBecX1#reference-kxr-y2z-zdb) of Alibaba Cloud. It can help you:

* integrate the CloudMonitor to your Monitoring System.
* leverage the power of PromQL, Alertmanager and Grafana(see [Screenshots](#)).
* analyze metrics however you want.
* save money. Api invocation is far cheaper than other services provided by CloudMonitor.

## Screenshots

![ecs](/static/img/ecs.png)

![rds](/static/img/rds.png)

Grafana Dashboards:

* ECS: https://grafana.com/dashboards/9455
* Telemetry: https://grafana.com/dashboards/9452
* ECS Instance: https://grafana.com/dashboards/9458
* RDS: https://grafana.com/dashboards/9461

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
> aliyun-exporter -p 9522 -c aliyun-exporter.yml
```

The default port is 9522, default config file location is `./aliyun-exporter.yml`.

Visit metrics in [localhost:9522/metrics](http://localhost:9522/metrics)

## Docker Image

Install
```bash
docker pull aylei/aliyun-exporter:0.0.1
```

To run the container, external configuration file is required:
```bash
docker run -p 9522:9522 -v $(pwd)/aliyun-exporter.yml:$(pwd)/aliyun-exporter.yml aylei/aliyun-exporter:0.0.1 -c $(pwd)/aliyun-exporter.yml
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
```

Notes:

* Find your target metrics in the [CloudMonitor Documentation](https://help.aliyun.com/document_detail/28619.html?spm=a2c4g.11186623.6.670.4cb92ea7URJUmT).
* CloudMonitor API has an rate limit, tuning the `rate_limit` configuration if the requests are rejected.
* CloudMonitor API also has an monthly quota for invocations (AFAIK, 5,000,000 invocations / month for free). Plan your usage in advance. 

> Given that you have 50 metrics to scrape with 60s scrape interval, about 2,160,000 requests will be set by the exporter for 30 days.

## Telemetry

Request success summary and failure summary are exposed in `cloudmonitor_request_latency_seconds` and `cloudmonitor_failed_request_latency_seconds`.

Each `Project-Metric` pair will have a corresponding metric named `aliyun_{project}_{metric}_up`, which indicates whether this metric are successfully scraped.

## Scale and HA Setup

The CloudMonitor API could be slow if you have large amount of resources. You can separate metrics over multiple exporter instances to scale.

For HA setup, simply duplicate your deployments: 2 * prometheus, and 2 * exporter for each prometheus.

> HA Setup will double your requests, which may run out your quota.

## Contribute

Feel free to open issues and pull requests. Besides, I am a golang and java programmer, this project is a practice for python. Let know if you have any advice for my code style or logic. Any feedback will be highly appreciated!

# 中文

阿里云云监控的 Prometheus Exporter. 

## 安装

```bash
pip3 install aliyun-exporter
```

## 使用

首先需要在配置文件中写明阿里云的 `Access Key` 以及需要拉取的云监控指标，例子如下：

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

启动 Exporter

```bash
> aliyun-exporter -p 9522 -c aliyun-exporter.yml
```

访问 [localhost:9522/metrics](http://localhost:9522/metrics) 查看指标抓取是否成功

## Docker 镜像

```bash
docker run -p 9522:9522 -v $(pwd)/aliyun-exporter.yml:$(pwd)/aliyun-exporter.yml aylei/aliyun-exporter:0.1.0 -c $(pwd)/aliyun-exporter.yml
```

## 配置

```yaml
rate_limit: 5 # 限流配置，每秒请求次数. 默认值: 10
credential:
  access_key_id: <YOUR_ACCESS_KEY_ID> # 必填
  access_key_secret: <YOUR_ACCESS_KEY_SECRET> # 必填
  region_id: <REGION_ID> # 默认值: 'cn-hangzhou'
  
metrics: # 必填, 目标指标配置
  acs_cdn: # 必填，云监控中定义的 Project 名字
  - name: QPS # 必填, 云监控中定义的指标名字
    rename: qps # 选填，定义对应的 Prometheus 指标名字，默认与云监控指标名字一致
    period: 60 # 选填，默认 60
    measure: Average # 选填，响应体中的指标值字段名，默认 'Average'
```

提示：

* [云监控-预设监控项参考](https://help.aliyun.com/document_detail/28619.html?spm=a2c4g.11186623.6.670.4cb92ea7URJUmT) 可以查询 Project 与对应的指标
* 云监控 API 有限流，假如被限流了可以调整限流配置
* 云监控 API 每月调用量前 500 万次免费，需要计划好用量

> 假如配置了 50 个指标，再配置 Prometheus 60秒 抓取一次 Exporter，那么 30 天大约会用掉 2,160,000 次请求

## 自监控

`cloudmonitor_request_latency_seconds` 和 `cloudmonitor_failed_request_latency_seconds` 中记录了对 CloudMonitor API 的调用情况。

每一个 CloudMonitor 指标都有一个对应的 `aliyun_{project}_{metric}_up` 来表明该指标是否拉取成功。

## 扩展与高可用

假如机器很多，云监控 API 可能比较慢，这时候可以把指标分拆多个 Exporter 实例中去。

HA 和 Prometheus 本身的 HA 方案一样，就是搭完全相同的两套监控。每套部署一台 Prometheus 加上对应的 Exporter。或者直接交给底下的 PaaS 设施来做 Standby。

> 部署两套会导致请求量会翻倍，要注意每月 API 调用量
