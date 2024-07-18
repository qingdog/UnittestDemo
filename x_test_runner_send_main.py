#!/usr/bin/env python
# _*_ coding:utf-8 _*_
__author__ = 'YinJia'

import configparser
import logging
import os
import sys
import time
import unittest

import loguru
# from loguru import logger
from XTestRunner import HTMLTestRunner

from logs.mylogging import MyLogging
from utils.get_new_report import get_latest_file_path
from utils.mail_util import send_mail


class MyConfig:
    BASE_DIR = os.path.dirname(__file__)
    sys.path.append(BASE_DIR)

    # 配置文件
    CONFIG_INI = os.path.join(BASE_DIR, "config.ini")
    # 测试数据
    TESTDATA_DIR = os.path.join(BASE_DIR, "testdata")
    # 测试用例模板文件
    TESTDATA_FILE = os.path.join(TESTDATA_DIR, "excel_test_case.xlsx")
    # 测试用例报告
    TESTREPORT_DIR = os.path.join(BASE_DIR, "report")
    # 测试用例程序文件
    TEST_CASE = os.path.join(BASE_DIR, "testcase")


def run_case(all_case, report_path=MyConfig.TESTREPORT_DIR):
    now = time.strftime("%Y%m%d")
    filename = report_path + '/' + f"result-{now}" + '.html'
    with open(filename, 'wb') as fp:
        loguru._level = "DEBUG"
        loguru._console_format = "{time} {level} {message}"
        # loguru._console_format = "<green>{time}</green> <level>{message}</level>"
        runner = HTMLTestRunner(stream=fp,
                                verbosity=2,
                                title='接口自动化测试报告',
                                tester='Jason',
                                description='环境：windows 10 浏览器：chrome',
                                language='zh-CN',
                                logger=loguru
                                )

        runner.run(all_case)

    # 最新测试报告文件的路径
    latest_file_path = get_latest_file_path(MyConfig.TESTREPORT_DIR)
    logging.getLogger().info("报告路径：" + latest_file_path)

    # 调用发送邮件模块
    config_p = configparser.ConfigParser()
    config_p.read(MyConfig.CONFIG_INI, encoding='utf-8')
    config_smtp = config_p.items("smtp")
    # 创建一个字典来存储SMTP配置
    smtp_config = {key: value for key, value in config_smtp}
    if "password" in smtp_config and smtp_config["password"] != "":
        send_mail(latest_file_path, smtp_config)


if __name__ == "__main__":
    """加载testcase目录下所有test开头的py文件"""
    cases = unittest.defaultTestLoader.discover(MyConfig.TEST_CASE, pattern='test*.py')
    run_case(cases)



