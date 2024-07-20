#!/usr/bin/env python
# _*_ coding:utf-8 _*_
__author__ = 'YinJia'

import ast
import logging
import re
import os, sys, json

import requests
import configparser as configparser

from urllib3 import PoolManager

sys.path.append(os.path.dirname(os.path.dirname(__file__)))


class MyRequests:
    configParser = configparser.ConfigParser()
    configParser.read(os.path.join(os.path.dirname(os.path.dirname(__file__)), "config.ini"),
                      encoding='UTF-8')
    headers = configParser.get("request", "headers")
    body = configParser.get("request", "body")

    def send_request(self, session: PoolManager, excel_data):
        # 从读取的表格中获取响应的参数作为传递
        url = excel_data["url"]
        method = excel_data["method"]

        if "params" in excel_data:
            params = ast.literal_eval(excel_data["params"]) if excel_data["params"] else None

        headers = ast.literal_eval(excel_data["headers"]) if excel_data["headers"] else eval(self.headers)
        if headers is dict:
            headers: dict
            content_type = headers.get("Content-Type")
            # if re.search("application/json", content_type) is None:
            #     headers = json.dumps(headers)

        body = ast.literal_eval(json.dumps(excel_data["body"])) if excel_data["body"] else eval(json.dumps(self.body))

        # 不忽略SSL证书验证
        # requests.packages.urllib3.disable_warnings(category=InsecureRequestWarning)
        response = session.request(method=method, url=url, headers=headers, data=body, verify=True)
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
