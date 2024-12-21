import logging
import os
import time
from locust import HttpUser, task, between, TaskSet, clients


# 定义一个任务类继承TaskSet类
class TaskSetDemo(TaskSet):

    # @task 是装饰器，声明此方法是一个任务，，权重默认为1
    @task
    def city_list(self):
        # self.client.get("/test-api/code")
        # self.client.get("/assets/login-background-dlh_CT3N.jpg")
        self.client.get("/app/applet/action/city/list")

    # @task
    # def project_reportable(self):
    #     self.client.get("/app/applet/project/reportable/91530523MACRB35DX2/1/15")

    # @task
    # def public_detail(self):
    #     self.client.get("/app/applet/public/detail/1821792987881213954/1821020653129764866")

    # @task(3) 是装饰器，声明此方法是一个任务，权重为3
    # @task(3)
    def view_items(self):
        for item_id in range(10):
            self.client.get(f"/item?id={item_id}", name="/item")
            time.sleep(1)

    # @task
    def view_index(self):
        with self.client.get("/", catch_response=True) as response:
            response: clients.ResponseContextManager
            logging.info(response.status_code)
            # if response.text != "Success":
            #     response.failure("Got wrong response")
            # elif response.elapsed.total_seconds() > 0.5:
            #     response.failure("Request took too long")


# 定义一个运行类继承HttpUser类
class HttpUserDemo(HttpUser):
    headers = {"Content-Type": "application/json;charset=utf-8",
               "authorization": "Bearer a.b.c"}

    # 声明执行的任务集是哪个类
    tasks = [TaskSetDemo]
    # 设置运行过程中间隔时间 返回一个介于min_wait和max_wait之间的随机数
    wait_time = between(1, 5)

    authorization = ["eyJhbGciOiJIUzUxMiJ9.eyJ1c2VyX2lkIjoxODIxMDIwNjUzMTI5NzY0ODY2fQ.ADHHcXkJxQ2-MDtam_6JE9PGA2rp8G4e5yQAuT8O1nhEMNjGphfyF0AGeEjOYtcx2lRtB7yVelhjcSFkSzxyJw",
                     "eyJhbGciOiJIUzUxMiJ9.eyJ1c2VyX2lkIjoxODIzMTg0MTA0NzYxNDgzMjY1fQ.5qFCFOmR7xezecyKY1mtmMfNy2kcfmUbLNK7IvkJr7zGXxGMJJIwel5s1gYWuCooHz1hYYuAphCSsy1c_qbBuw"]
    index = 1

    # 每用户初始动作，作用等同于pytest、unittest的setup
    def on_start(self):
        i = self.index % len(self.authorization)
        self.index += 1
        self.headers["authorization"] = f"{self.authorization[i]}"
        # self.client.post("/test-api/auth/login", json={"username": "admin", "password": "admin123", "code": "1",
        #                                                "uuid": "1199344940234ba89194b76b100bd760"})

    # 每用户结束动作，作用等同于pytest、unittest的teardown
    def on_stop(self):
        # self.client.delete("/test-api/auth/logout")
        self.client.close()


if __name__ == '__main__':
    """
    --headless	禁用Web界面，而是立即开始负载测试。需要指定-u 用户数 和-t 
    -t， --run-time 在指定的时间段后停止，例如（300s，20m，3h，1h30m等）。仅与–headless一起使用。默认为永久运行。
    """
    # os.system(
    #     "locust -f locust_test_task_set.py --headless --users 10 --run-time 5 --spawn-rate 1 -H http://192.168.50.202:9999")
    os.system("locust -f locust_test_task_set.py --users 8 --run-time 20s --spawn-rate 1 -H  https://test-lqc-api.liqicloud.com:443")

