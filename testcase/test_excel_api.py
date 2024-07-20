#!/usr/bin/env python
# _*_ coding:utf-8 _*_
__author__ = 'YinJia'

import ast
import configparser
import logging
import os

import certifi
import urllib3

from utils.xlrd_excel import XlrdExcel
from x_test_runner_send_main import MyConfig
import unittest, requests, ddt
from utils.my_requests import MyRequests
from utils.excel_testcase_processor import ExcelTestCaseProcessor


@ddt.ddt
class TestAPI(unittest.TestCase):
    """
    自动化测试excel中api
    """
    """
    该类用于读取指定的Excel测试用例文件，并对每个测试用例执行API请求，然后验证响应。
    测试用例文件路径定义在配置文件中，默认为 `testdata/auto_test_case.xlsx`。
    测试流程包括：
    - 从Excel文件中读取测试用例。
    - 发送HTTP请求。
    - 验证响应状态码。
    - 验证响应内容中的特定字段。
    类属性:
    - configParser: ConfigParser实例，用于读取配置文件。
    - config_status_codes: 期望的HTTP状态码列表。
    注意:
    - 请确保配置文件 `config.ini` 存在并且格式正确。
    - Excel文件中的测试用例应遵循特定的格式定义。
    - 日志配置需要在运行测试之前完成。
    """

    # 创建ConfigParser对象
    configParser = configparser.ConfigParser()

    # 读取配置文件
    config_file_path = os.path.join(os.path.dirname(os.path.dirname(__file__)), "config.ini")
    configParser.read(config_file_path, encoding='UTF-8')
    status_codes_str = configParser.get('request', 'status_code')
    # 将字符串分割成列表，并转换为整数
    config_status_codes = [int(code) for code in status_codes_str.split(',')]

    def setUp(self):
        self.session = requests.session()
        self.http = self.session
        # self.http = urllib3.PoolManager(
        #     cert_reqs="CERT_REQUIRED",
        #     ca_certs=certifi.where()
        # )

    def tearDown(self):
        pass

    logger = logging.getLogger()

    testData: list[dict[str, int]] = XlrdExcel(MyConfig.TESTDATA_FILE).read_data()
    # excel_data为sheet页中的一行数据，key为每一列的首行数据，value为这一行中的值
    @ddt.data(*ExcelTestCaseProcessor(MyConfig.TESTDATA_FILE).read_data())
    def test_api(self, excel_data: dict):
        """excel接口测试"""
        # 发送请求
        if "url" not in excel_data:
            return
        response = MyRequests().send_request(self.http, excel_data=excel_data)
        # 校验http响应的状态码
        url = excel_data["url"]
        if response.status_code not in self.config_status_codes:
            raise RuntimeError(
                f"{url} {response.status_code}")

        code_key = "code"
        if code_key in excel_data:
            code = excel_data[code_key]
        else:
            code_key = self.next_key(excel_data, "body")
            code = excel_data[code_key]

        msg_key = "msg"
        if msg_key in excel_data:
            msg = excel_data[msg_key]
        else:
            msg_key = self.next_key(excel_data, code_key)
            msg = excel_data[code_key]
        result = "PASS"

        case_id = ""
        if "id" in excel_data:
            case_id = excel_data["id"]
        title = ""
        if "title" in excel_data:
            title = excel_data["title"]

        # 检查响应的Content-Type是否为JSON
        content_type = response.headers.get('Content-Type', '')
        if 'application/json' in content_type:
            json = response.json()
            self.logger.debug(f"用例数据：{excel_data}")
            self.logger.info("响应数据：%s" % response.content.decode("utf-8"))

            try:
                self.assertEqual(ast.literal_eval(code), json[code_key], f"{case_id} {title} {url}")
                self.assertIn(msg, json[msg_key], f"{case_id} {title} {url}")
            except Exception as e:
                result = "FAIL"
                raise e
            finally:
                ExcelTestCaseProcessor(MyConfig.TESTDATA_FILE).write_data(excel_data, value=result)
        else:
            # 如果Content-Type不是JSON，处理非JSON响应
            try:
                self.assertIn(ast.literal_eval(code), response.text, f"{case_id} {title} {url}")
                self.assertIn(msg, response.text, f"{case_id} {title} {url}")
            except Exception as e:
                result = "FAIL"
                raise e
            finally:
                ExcelTestCaseProcessor(MyConfig.TESTDATA_FILE).write_data(excel_data, value=result)

    def next_key(self, my_dict, current_key):
        keys = list(my_dict.keys())
        if current_key not in keys:
            return None  # 如果当前键不在字典中，返回None
        current_index = keys.index(current_key)
        if current_index + 1 < len(keys):
            return keys[current_index + 1]  # 返回下一个键
        else:
            return None  # 如果当前键是最后一个，返回None


if __name__ == '__main__':
    unittest.main()
