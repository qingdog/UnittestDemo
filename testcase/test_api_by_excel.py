#!/usr/bin/env python
# _*_ coding:utf-8 _*_
__author__ = 'YinJia'

import ast
import configparser
import datetime
import io
import logging
import os, json
import re
import sys
import time

# from utils.xlrd_excel import XlrdExcel
from run_x_test_runner_send_main import MyConfig
import unittest, requests, ddt

from utils.excel_testcase_util import ExcelTestCaseProcessor
import jsonpath_ng

from utils.login_ruoyi_verification_code import login_verification_code


@ddt.ddt
class TestAPI(unittest.TestCase):
    """
    自动化测试最新excel文件中的api `testdata/new.xlsx`
    """
    status_codes_str = os.getenv("status_code")
    code_default = os.getenv("code")
    body_default = os.getenv("body")
    headers = os.getenv("headers")
    base_url = os.getenv("base_url")
    method = os.getenv("method")
    # 将字符串分割成列表，并转换为整数
    config_status_codes = [int(code) for code in status_codes_str.split(',')]
    session = None

    @classmethod
    def setUpClass(cls):
        cls.session = requests.session()
        """根据验证码进行登录"""
        token = login_verification_code()
        # 字符串转dict
        cls.headers = eval(cls.headers)
        if token and isinstance(cls.headers, dict):
            cls.headers["authorization"] = f"Bearer {token}"

    @classmethod
    def tearDownClass(cls):
        cls.session.close()
        pass

    def setUp(self):
        pass

    def tearDown(self):
        pass

    is_repair_print = True

    def repair_print(self, message, end="\n", flush=True):
        """修复x-test-runner框架每次print输出都会换行的问题"""
        original_stdout = sys.stdout

        class MyOutput:
            def write(self, message):
                # 将消息输出到标准输出，不添加换行
                sys.__stdout__.write(f'{message}')

            def flush(self):
                pass  # 需要实现flush方法以兼容stdout

        # 替换sys.stdout
        sys.stdout = MyOutput()
        # 使用示例
        print(message, end=end, flush=flush)  # 不会换行
        # sys.stdout = original_stdout

    logger = logging.getLogger()

    def package_send_data(self, excel_data):
        """封装excel中需要发送请求的数据"""
        if "url" not in excel_data or excel_data["url"] == " " or excel_data["url"] == "" or excel_data["url"] is None:
            return None, None, None

        headers = ast.literal_eval(excel_data["headers"]) if excel_data["headers"] else self.headers
        if headers is dict:
            headers: dict
            content_type = headers.get("Content-Type")
            # if re.search("application/json", content_type) is None:
            #     headers = json.dumps(headers)

        body: str = ast.literal_eval(json.dumps(excel_data["body"])) if excel_data["body"] else eval(
            json.dumps(self.body_default))

        # 处理非完整url
        url = excel_data["url"]
        if re.search(r"^http(s)?://", url) is None:
            if not url.startswith("/"):
                url = "/" + url
            url = self.base_url + url

        method = excel_data["method"]
        method = self.method if method is None else method

        # 暂时不处理params
        # if "params" in excel_data:
        #     params = ast.literal_eval(excel_data["params"]) if excel_data["params"] else None

        return method, url, headers, body

    # testData: list[dict[str, int]] = XlrdExcel(MyConfig.TESTDATA_FILE).read_data()
    # excel_data为sheet页中的一行数据，key为每一列的首行数据，value为这一行中的值
    # @ddt.data(*testData)
    @ddt.data(*ExcelTestCaseProcessor(MyConfig.TESTDATA_FILE).read_data())
    def test_api(self, excel_data: dict):
        """TestAPI.test_api"""
        body = ""
        result = "PASS"
        try:
            if self.is_repair_print:
                self.is_repair_print = False
                self.repair_print("", end="")

            if "result" in excel_data and "PASS" == excel_data["result"]: return
            # 如果这一行用例中没有url则跳过
            if "url" not in excel_data or excel_data["url"] is None:
                return

            method, url, headers, body = self.package_send_data(excel_data)
            # 使用全局变量进行替换
            body = self.replace_body_variables(body)
            url = self.replace_body_variables(url)

            # 发起请求
            try:
                response = self.session.request(method=method, url=url, headers=headers, data=body, verify=True)
            except requests.exceptions.SSLError as e:
                # 忽略SSL证书验证
                # requests.packages.urllib3.disable_warnings(category=InsecureRequestWarning)
                response = self.session.request(method=method, url=url, headers=headers, data=body, verify=False)
                logging.getLogger("mylogging").warning(f"警告 未经过证书验证请求：{url}")
            except Exception as e:
                raise e

            if response.status_code not in self.config_status_codes:
                # self.assertEqual(self.config_status_codes[0], response.status_code, f"{response.status_code} {url}")
                raise RuntimeError(f"状态码校验失败！{url} {response.status_code}")

            case_id, title, msg, variable_key, variable = self.get_excel_data(excel_data, url)

            # 检查响应的Content-Type是否为JSON
            content_type = response.headers.get('Content-Type', '')
            if 'application/json' in content_type:
                res_json = response.json()

                # 提取json格式响应数据到全局变量（多个使用逗号分割）
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

                # 暂时不校验code
                # if not code:
                #     code = self.code_default
                # self.assertEqual(ast.literal_eval(code), json[code_key], f"{case_id} {title} {url}")
                # 后端响应消息提示
                # self.assertIn(msg, json[msg_key], f"{case_id} {title} {url}")
                if msg.startswith("!"):
                    msg = msg[1:]
                    self.assertNotIn(msg, response.content.decode("utf-8"), f"{case_id} {title} {url}")
                else:
                    self.assertIn(msg, response.content.decode("utf-8"), f"{case_id} {title} {url}")
            else:  # 如果Content-Type不是JSON，处理非JSON响应
                # self.assertIn(ast.literal_eval(code), response.text, f"{case_id} {title} {url}")
                self.assertIn(msg, response.text, f"{case_id} {title} {url}")
            # 检查是否存在 'delay' 键
            if "delay" in excel_data:
                delay = excel_data["delay"]  # 获取延迟时间
                self.delay_print(delay)
        except Exception as e:
            result = "FAIL"
            logging.warning(f"请求参数：{body}")
            raise e
        finally:
            ExcelTestCaseProcessor(MyConfig.TESTDATA_FILE).write_data(excel_data, value=result)

    def delay_print(self, delay):
        if not delay:  # 确保延迟时间存在且不为空
            return
        try:
            # 转换字符串为浮点数，并进行延迟
            delay_seconds = float(delay)
            print(f"正在睡眠{delay_seconds}秒", end="", flush=True)
            for _ in range(int(delay_seconds)):
                print(".", end="", flush=True)  # 每秒打印一个点，不换行
                time.sleep(1)  # 每次延迟一秒
            print()  # 默认换行
            # 处理非整数秒的情况（如果delay_seconds有小数部分）
            remainder = delay_seconds - int(delay_seconds)
            if remainder > 0:
                time.sleep(remainder)
        except ValueError as e:
            raise RuntimeError(e, f"延迟值无效，无法转换为数字！")

    def get_excel_data(self, excel_data, url):
        """获取excel数据用于校验"""
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

        case_id = ""
        if "id" in excel_data:
            case_id = excel_data["id"]

        # 测试报告用例描述
        title = ""
        if "title" in excel_data:
            title = excel_data["title"]
            self._testMethodDoc = f"{title} {url}"

        variable_key = "variable"
        if variable_key in excel_data:
            variable: str = excel_data["variable"]
        else:
            variable_key = self.next_key(excel_data, "result")
            variable = excel_data[variable_key]

        return case_id, title, msg, variable_key, variable

    def next_key(self, my_dict, current_key):
        """从指定的key中找到下一个key"""
        keys = list(my_dict.keys())
        if current_key not in keys:
            return None  # 如果当前键不在字典中，返回None
        current_index = keys.index(current_key)
        if current_index + 1 >= len(keys):
            return None  # 如果当前键是最后一个，返回None
        return keys[current_index + 1]  # 返回下一个键

    def replace_body_variables(self, input_string):
        """正则匹配类似 ${variable1} 的占位符（可替换多个）"""
        pattern = r"\${([a-zA-Z_][\w]*)}"  # 构造变量格式${variable1}

        # 替换占位符为 variables 中的实际值
        def replacer(match):
            var_name = match.group(1)  # 获取变量名
            result = self.variables.get(var_name, match.group(0))  # 没有替换则返回全部原始字符
            logging.info(f"变量替换：{var_name} => {result}")
            return result

        return re.sub(pattern, replacer, input_string)

    def extract_variable_using_jsonpath(self, res_json, jsonpath_expression="$.data.list[0].id"):
        """使用jsonpath表达式从响应json中提取值返回 保存成变量"""
        jsonpath_expr = jsonpath_ng.parse(jsonpath_expression)
        matches = jsonpath_expr.find(res_json)
        if matches:
            # 转成字符串类型用于正则替换
            extract_variable = str(matches[0].value)
            logging.info(f"提取变量：{len(self.variables) + 1} => {extract_variable}")
            return extract_variable
        return None

    variables = {}

    # 废弃方法
    def replace_variables_discard(self, input_string):
        """替换字符串中的占位符"""
        for var_name in self.variables.keys():
            # placeholder = f"${{{var_name}}}"
            placeholder = "${%s}" % var_name  # 构造变量格式${variable1}
            if placeholder in input_string:
                input_string = input_string.replace(placeholder, str(self.variables[var_name]))
                logging.info(f"变量替换：{placeholder} => {self.variables[var_name]}")
        return input_string

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


if __name__ == '__main__':
    unittest.main()
