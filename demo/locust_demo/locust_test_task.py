# locust_test_task.py
import os

from locust import HttpUser, task


class TestLocust01(HttpUser):
    @task
    def demo_code(self):
        self.client.get("/test-api/code")
        self.client.get("/assets/login-background-dlh_CT3N.jpg")


if __name__ == '__main__':
    """
    --headless	禁用Web界面，而是立即开始负载测试。需要指定-u 用户数 和-t 
    -t， --run-time 在指定的时间段后停止，例如（300s，20m，3h，1h30m等）。仅与–headless一起使用。默认为永久运行
    --spawn-rate 1 设置每秒启动的用户数量。这里设置为每秒1个用户
    """
    os.system("locust -f locust_test_task.py --users 10 --run-time 20s --spawn-rate 1 -H http://192.168.50.202:9999")
