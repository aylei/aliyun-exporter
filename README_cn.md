# 阿里云 Exporter

![license](https://img.shields.io/hexpm/l/plug.svg)
[![help wanted](https://img.shields.io/github/issues/aylei/aliyun-exporter/help%20wanted.svg)](https://github.com/aylei/aliyun-exporter/issues?q=is%3Aissue+is%3Aopen+label%3A%22help+wanted%22)
[![pypi](https://img.shields.io/pypi/v/aliyun-exporter.svg)](https://pypi.org/project/aliyun-exporter/)
[![docker](https://img.shields.io/docker/pulls/aylei/aliyun-exporter.svg)](https://cloud.docker.com/u/aylei/repository/docker/aylei/aliyun-exporter)
[![Build Status](https://travis-ci.org/aylei/aliyun-exporter.svg?branch=master)](https://travis-ci.org/aylei/aliyun-exporter)

阿里云云监控的 Prometheus Exporter. 


## 截图

![gif](/static/img/stack.gif)

[more screenshots here](./screenshots.md)

## 快速开始

从 0.3.0 版本开始, 项目里提供了一个 docker-compose stack 来从零到一地构建一整套针对阿里云的监控告警系统(当然你也可以继续扩展这套系统来适配自有的IDC以及业务监控). 

安装方式:

首先安装好 docker 1.17 以上版本, 安装方式可以自行 GG

接下来运行以下命令:

```bash
git clone git@github.com:aylei/aliyun-exporter.git
cd docker-compose
ALIYUN_ACCESS_ID=YOUR_ACCESS_ID ALIYUN_ACCESS_SECRET=YOUR_ACCESS_KEY docker-compose up
```

看到各个组件的启动日志基本滚完之后, 就可以访问 [localhost:3000](http://localhost:3000) 来探索 Grafana 看板了.

更多的配置项请见 [Docker Compose](#docker-compose)

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
> aliyun-exporter -p 9525 -c aliyun-exporter.yml
```

访问 [localhost:9525/metrics](http://localhost:9525/metrics) 查看指标抓取是否成功

## Docker 镜像

```bash
docker run -p 9525:9525 -v $(pwd)/aliyun-exporter.yml:$(pwd)/aliyun-exporter.yml aylei/aliyun-exporter:0.3.0 -c $(pwd)/aliyun-exporter.yml
```

## Grafana 看板

预配置了一些 Grafana 看板. 见[Screenshots](#screenshots)

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

## 特殊的 Project

有一些指标没有在云监控 API 中暴露, 为了保持配置的一致性, 我们定义了一些特殊 Project 来配置这些指标.

所有的特殊 Project:

* `rds_performance`: RDS 的详细性能数据, 可选的指标名可以在这里找到: [性能参数表](https://help.aliyun.com/document_detail/26316.html?spm=a2c4g.11186623.4.3.764b2c01QbzUdY)

## 自监控

`cloudmonitor_request_latency_seconds` 和 `cloudmonitor_failed_request_latency_seconds` 中记录了对 CloudMonitor API 的调用情况。

每一个 CloudMonitor 指标都有一个对应的 `aliyun_{project}_{metric}_up` 来表明该指标是否拉取成功。

# Docker Compose

`./docker-compose` 目录下存放了整个 docker-compose stack, 这一套系统包含以下组件:

* aliyun-exporter (就是本项目): 负责拉取阿里云的监控指标和资源信息
* [Prometheus](https://github.com/prometheus/prometheus): 负责存储指标以及计算警报
* [Alertmanager](https://github.com/prometheus/alertmanager): 负责警报路由和警报通知
* [Grafana](https://github.com/grafana/grafana): 展现监控看板
* [prometheus-webhook-dingtalk](https://github.com/timonwong/prometheus-webhook-dingtalk): 为 Alertmanager 集成钉钉消息通知

```bash
# 配置 prometheus 的外部地址, 从警报跳转到详情时会用到, 需要外部可访问
export PROMETHEUS_HOST=YOUR_PUBLIC_IP_OR_HOSTNAME
# 配置钉钉机器人的 Token, 可以自行 GG 怎么创建钉钉机器人
export DINGTALK_TOKEN=YOUR_DINGTALK_ROBOT_TOEKN
# 配置阿里云 exporter 需要的验证信息
export ALIYUN_REGION=YOUR_REGION
export ALIYUN_ACCESS_ID=YOUR_ID
export ALIYUN_ACCESS_SECRET=YOUR_SECRET
# 后台运行整套系统
docker-compose up -d
```

启动后:

* Grafana 默认监听 3000 端口
* Alertmanager 默认监听 9093 端口
* Prometheus 默认监听 9090 端口

启动之后, 预设的警报规则就会开始计算, 因此假如配置正确的话, 你可能会收到一些钉钉报警.

你可以修改 `./docker-compose/{component}` 里的配置文件来自由配置各个组件, 有问题可以 GG 或者在 issue 里提问.

假如你自己制定了一些看板和警报规则, 非常欢迎你把它们贡献到项目里!

## 扩展与高可用

假如机器很多，云监控 API 可能比较慢，这时候可以把指标分拆多个 Exporter 实例中去。

HA 和 Prometheus 本身的 HA 方案一样，就是搭完全相同的两套监控。每套部署一台 Prometheus 加上对应的 Exporter。或者直接交给底下的 PaaS 设施来做 Standby。

> 部署两套会导致请求量会翻倍，要注意每月 API 调用量

## 贡献

我们欢迎 PR 或 issue 等任何形式的贡献! 你也可以在 [`help wanted`](https://github.com/aylei/aliyun-exporter/issues?q=is%3Aissue+is%3Aopen+label%3A%22help+wanted%22) label 下找到适合开始贡献的 issue!