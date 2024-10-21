#!/usr/bin/env python
# _*_ coding:utf-8 _*_
__author__ = 'YinJia'

import ast
import configparser
import logging
import os, json
import re
import time

# from utils.xlrd_excel import XlrdExcel
from run_x_test_runner_send_main import MyConfig
import unittest, requests, ddt

from utils import verification_code_login
from utils.my_requests import MyRequests
from utils.excel_testcase_processor import ExcelTestCaseProcessor
import jsonpath_ng


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
    code_default = configParser.get('request', 'code')
    body_default = configParser.get("request", "body")
    headers = configParser.get("request", "headers")

    # 将字符串分割成列表，并转换为整数
    config_status_codes = [int(code) for code in status_codes_str.split(',')]

    @classmethod
    def setUpClass(cls):
        """根据验证码进行登录"""
        h = verification_code_login.main()
        if h:
            cls.headers = h
            pass
        else:
            cls.headers = eval(cls.headers)

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

    # testData: list[dict[str, int]] = XlrdExcel(MyConfig.TESTDATA_FILE).read_data()
    # excel_data为sheet页中的一行数据，key为每一列的首行数据，value为这一行中的值
    # @ddt.data(*testData)
    @ddt.data(*ExcelTestCaseProcessor(MyConfig.TESTDATA_FILE).read_data())
    def test_api(self, excel_data: dict):
        """TestAPI.test_api"""
        # if "result" in excel_data and "PASS".__eq__(excel_data["result"]): return

        if "url" not in excel_data or excel_data["url"] == " " or excel_data["url"] == "" or excel_data["url"] is None:
            return

        headers = ast.literal_eval(excel_data["headers"]) if excel_data["headers"] else self.headers
        if headers is dict:
            headers: dict
            content_type = headers.get("Content-Type")
            # if re.search("application/json", content_type) is None:
            #     headers = json.dumps(headers)

        body: str = ast.literal_eval(json.dumps(excel_data["body"])) if excel_data["body"] else eval(
            json.dumps(self.body_default))
        # 使用全局变量进行替换
        body = self.replace_body_variables(body)

        url = excel_data["url"]
        url = self.replace_body_variables(url)

        # 检查是否存在 'delay' 键
        if "delay" in excel_data:
            delay = excel_data["delay"]  # 获取延迟时间
            if delay:  # 确保延迟时间存在且不为空
                try:
                    # 转换字符串为浮点数，并进行延迟
                    delay_seconds = float(delay)
                    time.sleep(delay_seconds)  # 延迟操作
                except ValueError as e:
                    raise RuntimeError(e, f"延迟值无效，无法转换为数字！")

        # 发起请求
        response = MyRequests().send_request(self.http, excel_data=excel_data, url=url, body=body, headers=headers)
        # 校验http响应的状态码
        url = excel_data["url"]
        self.assertEqual(self.config_status_codes[0], response.status_code, f"{response.status_code} {url}")
        # if response.status_code not in self.config_status_codes:
        #     raise RuntimeError(
        #         f"{url} {response.status_code}")

        code_key = "code"
        if code_key in excel_data:
            code = excel_data[code_key]
        else:
            code_key = self.next_key(excel_data, "body")
            code = excel_data[code_key]

        msg_key = "msg"
        if msg_key in excel_data:
            msg: str = excel_data[msg_key]
        else:
            msg_key = self.next_key(excel_data, code_key)
            msg = excel_data[code_key]
        result = "PASS"

        case_id = ""
        if "id" in excel_data:
            case_id = excel_data["id"]

        # 测试报告用例描述
        title = ""
        if "title" in excel_data:
            title = excel_data["title"]
            self._testMethodDoc = title + " " + url

        variable_key = "variable"
        if variable_key in excel_data:
            variable: str = excel_data["variable"]
        else:
            variable_key = self.next_key(excel_data, "result")
            variable = excel_data[variable_key]

        # 检查响应的Content-Type是否为JSON
        content_type = response.headers.get('Content-Type', '')
        if 'application/json' in content_type:
            res_json = response.json()

            # 使用逗号分割，提取响应结果到全局变量
            if variable:
                # json_dict2 = json.loads(res_json)
                variable_arr = variable.split(",")
                for vari in variable_arr:
                    extract_variable = self.extract_variable_using_jsonpath(res_json, jsonpath_expression=vari)
                    self.variables[f"{variable_key}{len(self.variables) + 1}"] = extract_variable

                # if isinstance(res_json, dict):
                #     self.get_veal_variable(res_json, variable)

            self.logger.debug(f"用例数据：{excel_data}")
            self.logger.info(f"{url} 响应数据：%s" % response.content.decode("utf-8"))

            try:
                if not code:
                    code = self.code_default
                # self.assertEqual(ast.literal_eval(code), json[code_key], f"{case_id} {title} {url}")
                # 后端响应消息提示
                # self.assertIn(msg, json[msg_key], f"{case_id} {title} {url}")
                if msg.startswith("!"):
                    msg = msg[1:]
                    self.assertNotIn(msg, response.content.decode("utf-8"), f"{case_id} {title} {url}")
                else:
                    self.assertIn(msg, response.content.decode("utf-8"), f"{case_id} {title} {url}")

            except Exception as e:
                result = "FAIL"
                logging.warning(f"请求参数：{body}")
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
        """从指定的key中找到下一个key"""
        keys = list(my_dict.keys())
        if current_key not in keys:
            return None  # 如果当前键不在字典中，返回None
        current_index = keys.index(current_key)
        if current_index + 1 >= len(keys):
            return None  # 如果当前键是最后一个，返回None
        return keys[current_index + 1]  # 返回下一个键

    def get_value_from_dict(self, data_dict, key):
        """【废弃】将 key 按 '.' 分割"""
        keys = key.split('.')

        # 逐级提取字典或列表中的值
        value = data_dict
        for k in keys:
            # 如果是数字，说明我们要访问列表中的元素
            if isinstance(value, list):
                try:
                    value = value[int(k)]
                except (ValueError, IndexError):
                    return None  # 如果无法转换成索引或索引超出范围
            elif isinstance(value, dict):
                value = value.get(k, None)
            else:
                return None  # 如果遇到非字典、非列表的值，直接返回 None
            if value is None:
                return None
        return value

    def get_veal_variable(self, json_dict, variable):
        """【废弃】提取响应数据并存储到全局变量中"""
        try:
            result = self.get_value_from_dict(json_dict, key=variable)
            self.variables[f"variable{len(self.variables) + 1}"] = result
        except Exception as e:
            raise e
        finally:
            pass

    def replace_body_variables(self, input_string):
        """正则匹配类似 ${variable1} 的占位符（可替换多个）"""
        pattern = r"\${([a-zA-Z_][\w]*)}"

        # 替换占位符为 variables 中的实际值
        def replacer(match):
            var_name = match.group(1)  # 获取变量名
            result = self.variables.get(var_name, match.group(0))  # 没有替换则返回全部原始字符
            logging.info(f"变量替换：{var_name} => {result}")
            return result

        return re.sub(pattern, replacer, input_string)

    def replace_body_variables2(self, input_string):
        """替换字符串中的占位符"""
        for var_name in self.variables.keys():
            # ${{表示${
            placeholder = f"${{{var_name}}}"
            if placeholder in input_string:
                input_string = input_string.replace(placeholder, str(self.variables[var_name]))
                logging.info(f"变量替换：{placeholder} => {self.variables[var_name]}")
        return input_string

    def extract_variable_using_jsonpath(self, res_json, jsonpath_expression):
        jsonpath_expr = jsonpath_ng.parse(jsonpath_expression)
        matches = jsonpath_expr.find(res_json)
        if matches:
            # 转成字符串类型用于正则替换
            extract_variable = str(matches[0].value)
            logging.info(f"提取变量：{len(self.variables)+1} => {extract_variable}")
            return extract_variable
        return None

    variables = {}


if __name__ == '__main__':
    unittest.main()
