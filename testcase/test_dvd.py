import inspect
import logging
import os
import unittest
import requests
from ddt import ddt, file_data, unpack  # 1、安装好ddt后导入

from api.apiList import ApiList


# from ddt_demo.common.mylog import mylog
# from ddt_demo.common.mylogging import Mylogging
# from ddt_demo.common.mylogger import MyLogger

@ddt  # 2、使用ddt标识
class TestDvd(unittest.TestCase):
    # log = mylog(os.path.basename(__file__))
    # logger = Mylogging().logger
    logger = logging.getLogger()

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
    def test_login(self, title, level, user, password, code, body):  # 引用yaml用例里各标题，数量需要对得上
        # try:
        if level == "H":
            # print("开始执行用例：", title)
            # self.log.info(f"开始执行用例：{title}")
            self.logger.info(f"开始执行用例：{title}")
            # logging.getLogger("123").warning(f"开始执行用例：{title}")

            # self.log.info("start test...22222222222222222.")
            # self.log.info("start test...111111111.")

            res = self.login(user, password)

            self.assertEqual(code, res.status_code)
            self.assertEqual(code, dict(res.json())["code"])

            # mylog(os.path.basename(__file__)).info("error...")

            # 进行断言
            self.assertIn(str(body), res.text)
        else:
            self.logger.warning(f"File \"{__file__}\", line 1 不执行：{title}")
            # self.logger.warning(f"{__file__}:65 {title} 不执行！")

    # except Exception as e:
    #     # self.log.error(e)
    #     self.logger.error("", exc_info=True)
    #
    #     # raise RuntimeError("新的异常信息") from e
    #     self.fail(e)


if __name__ == '__main__':
    unittest.main()
