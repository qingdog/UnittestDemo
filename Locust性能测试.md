Locust 是使用 Python 语言编写的开源性能测试工具，其简洁、轻量、高效的并发机制基于 Gevent 协程，可以实现单机模拟生成较高的并发压力。使用该工具可以节省实际的物理机资源，通过单机达到并发的效果，从而进行压力测试，找到最大的承压点。Locust 用于对网站（或其他系统）进行负载测试，并确定系统可以处理多少个并发用户。

## 一、安装
```shell
安装方式：
pip3 install locust
```
```shell
查看安装版本：
locust -V
```
> locust 2.31.4 from D:\Users\Administrator\AppData\Local\Programs\Python\Python312\Lib\site-packages\locust (Python 3.12.4, OpenSSL 3.0.13)

## 二、快速开始
1、web UI 模式
UI 模式可以直接在浏览器上配置要压测的用户数，以及每秒产生的用户数等等信息，比较直观方便。如下所示：

```python
#test_locust_01.py

from locust import HttpUser, task

class HelloWorldUser(HttpUser):
    @task
    def hello_world(self):
        self.client.get("/test-api/code")
        self.client.get("/assets/login-background-dlh_CT3N.jpg")
```
```shell
打开命令行，运行脚本（默认需在浏览器web端启动）：

locust -f test_locust_01.py
```
> [2024-08-30 16:34:49,729] QC134/INFO/locust.main: Starting web interface at http://localhost: 8089 (accepting connections from all network interfaces)
> 
> [2024-08-30 16:34:49,754] QC134/INFO/locust.main: Starting Locust 2.31.4

* 无头模式
```shell
locust -f test_locust_01.py --users 10 --run-time 20s --spawn-rate 1 -H http://192.168.50.202:9999
#测试持续时间（秒）= 804 / 40.34 ≈ 19.91 秒


[2024-08-31 11:09:12,169] QC134/INFO/locust.main: Shutting down (exit code 0)
Type     Name                                                                          # reqs      # fails |    Avg     Min     Max    Med |   req/s  failures/s
--------|----------------------------------------------------------------------------|-------|-------------|-------|-------|-------|-------|--------|-----------
GET      /assets/login-background-dlh_CT3N.jpg                                            397     0(0.00%) |    313      49    1424    300 |   19.92        0.00
GET      /test-api/code                                                                   407     0(0.00%) |     70      12     370     71 |   20.42        0.00
--------|----------------------------------------------------------------------------|-------|-------------|-------|-------|-------|-------|--------|-----------
         Aggregated                                                                       804     0(0.00%) |    190      12    1424    110 |   40.34        0.00

Response time percentiles (approximated)
Type     Name                                                                                  50%    66%    75%    80%    90%    95%    98%    99%  99.9% 99.99%   100% # reqs
--------|--------------------------------------------------------------------------------|--------|------|------|------|------|------|------|------|------|------|------|------
GET      /assets/login-background-dlh_CT3N.jpg                                                 300    370    420    460    520    620    680    830   1400   1400   1400    397
GET      /test-api/code                                                                         71     85     94    100    120    130    140    170    370    370    370    407
--------|--------------------------------------------------------------------------------|--------|------|------|------|------|------|------|------|------|------|------|------
         Aggregated                                                                            110    230    300    340    460    520    620    670   1400   1400   1400    804
```

## 六、分布式运行
```shell
#指定宿主机，并启动压测脚本
locust -f my_locustfile.py --master
```
```shell
ipconfig
Windows IP 配置


以太网适配器 以太网:

   连接特定的 DNS 后缀 . . . . . . . :
   本地链接 IPv6 地址. . . . . . . . : fe80::bf97:9f5e:457d:2e68%6
   IPv4 地址 . . . . . . . . . . . . : 192.168.40.171
   子网掩码  . . . . . . . . . . . . : 255.255.255.0
   默认网关. . . . . . . . . . . . . : 192.168.40.1
```

```shell
#指定压力机，并启动压测脚本
locust -f my_locustfile.py --worker --master-host=192.168.40.171

```
