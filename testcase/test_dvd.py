import inspect
import logging
import os
import traceback
import unittest
import requests
from ddt import ddt, file_data, unpack, data  # 1、安装好ddt后导入

from api.apiList import ApiList
from run_x_test_runner_send_main import MyConfig
from loguru import logger


# from ddt_demo.common.mylog import mylog
# from ddt_demo.common.mylogging import Mylogging
# from ddt_demo.common.mylogger import MyLogger

@ddt  # 2、使用ddt标识
class TestDvd(unittest.TestCase):
    """得有店接口测试"""
    # log = mylog(os.path.basename(__file__))
    # mylogger = Mylogging().logger
    mylogger = logging.getLogger()

    api_list = ApiList()  # 实例化接口
    dvd_headers = api_list.get_dvd_headers()

    login_api = api_list.get_dvd_login()  # 获取接口地址
    dvd_login_yml = "../testdata/dvd_login.yml"

    def login(self, username, password):
        body = {
            "mobile": username,
            "pass_word": password,
            "channel": 11
        }
        res = requests.post(url=self.login_api, json=body, headers=self.dvd_headers)
        return res

    # 进行断言
    @file_data(dvd_login_yml)  # 指定具体路径的用例，读之前需先装好 pyyarm 第三方模块
    @unpack  # 数据解包
    # @logger.catch
    def test_login(self, title, level, user, password, code, body):  # 引用yaml用例里各标题，数量需要对得上
        """
        TestDvd.test_login
        """
        self._testMethodDoc = title
        # try:
        if level == "H":
            self.mylogger.info(f"开始执行用例：{title}")
            print("1", end="")
            print("3", end="\n")

            res = self.login(user, password)

            self.assertEqual(code, res.status_code)
            self.assertEqual(code, dict(res.json())["code"])

            # 进行断言
            self.assertIn(str(body), res.text)
        else:
            self.mylogger.warning(f"File \"{__file__}\", line 1 不执行：{title}")

    # except Exception as e:
    #     # self.log.error(e)
    #     self.mylogger.error("", exc_info=True)
    #
    #     # raise RuntimeError("新的异常信息") from e
    #     self.fail(e)


if __name__ == '__main__':
    unittest.main()
