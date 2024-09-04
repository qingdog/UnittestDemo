#!/usr/bin/env python
# _*_ coding:utf-8 _*_
__author__ = 'YinJia'

import ast
import logging
import re
import os, sys, json

import requests
import configparser as configparser

import urllib3
from urllib3 import PoolManager
from urllib3.exceptions import SSLError

sys.path.append(os.path.dirname(os.path.dirname(__file__)))


class MyRequests:
    configParser = configparser.ConfigParser()
    configParser.read(os.path.join(os.path.dirname(os.path.dirname(__file__)), "config.ini"),
                      encoding='UTF-8')
    headers = configParser.get("request", "headers")
    body = configParser.get("request", "body")

    method = configParser.get("request", "method")
    base_url = configParser.get("request", "base_url")

    # def send_request(self, session: PoolManager, excel_data):
    def send_request(self, session: requests.sessions.Session, excel_data):
        # 从读取的表格中获取响应的参数作为传递
        url = excel_data["url"]
        # 处理非完整url
        if re.search("^http(s)?://", url) is None:
            if not url.startswith("/"):
                url = "/" + url
            url = self.base_url + url

        method = excel_data["method"]
        method = self.method if method is None else method

        if "params" in excel_data:
            params = ast.literal_eval(excel_data["params"]) if excel_data["params"] else None

        headers = ast.literal_eval(excel_data["headers"]) if excel_data["headers"] else eval(self.headers)
        if headers is dict:
            headers: dict
            content_type = headers.get("Content-Type")
            # if re.search("application/json", content_type) is None:
            #     headers = json.dumps(headers)

        body = ast.literal_eval(json.dumps(excel_data["body"])) if excel_data["body"] else eval(json.dumps(self.body))

        try:
            response = session.request(method=method, url=url, headers=headers, data=body, verify=True)
        except requests.exceptions.SSLError as e:
            # 忽略SSL证书验证
            # requests.packages.urllib3.disable_warnings(category=InsecureRequestWarning)
            response = session.request(method=method, url=url, headers=headers, data=body, verify=False)
            logging.getLogger("mylogging").warning(f"警告 未经过证书验证请求：{url}")
        except Exception as e:
            raise e

        return response


if __name__ == '__main__':
    config_p = configparser.ConfigParser()
    config_p.read(os.path.join(os.path.dirname(os.path.dirname(__file__)), "config.ini"),
                  encoding='UTF-8')
    print(config_p.items('smtp'))
    config_smtp = config_p.items("smtp")
    # 创建一个字典来存储SMTP配置
    smtp_config = {key: value for key, value in config_smtp}
    print(smtp_config)
