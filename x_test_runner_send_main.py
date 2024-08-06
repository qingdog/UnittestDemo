#!/usr/bin/env python
# _*_ coding:utf-8 _*_
__author__ = 'YinJia'

import configparser
import datetime
import functools
import logging
import os
import re
import sys
import time
import unittest

# import loguru
import XTestRunner
from XTestRunner.htmlrunner.result import _TestResult

from logs.mylogging import MyLogging, ColoredFormatter
from utils.myutil import get_latest_file_path
from utils.mail_util import send_mail


class MyConfig:
    FILE_DIR = os.path.dirname(__file__)
    sys.path.append(FILE_DIR)

    # 配置文件
    CONFIG_INI = os.path.join(FILE_DIR, "config.ini")
    # 测试数据
    TESTDATA_DIR = os.path.join(FILE_DIR, "testdata")

    # 测试用例报告
    TESTREPORT_DIR = os.path.join(FILE_DIR, "reports")
    # 测试用例程序文件
    TEST_CASE = os.path.join(FILE_DIR, "testcase")

    # 测试用例模板文件
    # 首先尝试在TESTDATA_DIR中查找.xlsx文件
    xlsx_files = [file for file in os.listdir(TESTDATA_DIR) if re.search("\\.xlsx?$", file)]
    # 如果在TESTDATA_DIR中没有找到，则在FILE_DIR中查找
    if not xlsx_files:
        xlsx_files = [file for file in os.listdir(FILE_DIR) if file.endswith('.xlsx')]
    # 如果找到了.xlsx文件，则设置TESTDATA_FILE
    # if xlsx_files:
    TESTDATA_FILE = os.path.join(TESTDATA_DIR if xlsx_files else FILE_DIR, xlsx_files[0])


class MyTestResult(_TestResult):
    def addFailure(self, test, err):
        super().addFailure(test, err)
        if self.verbosity >= 3:
            MyLogging.getLogger().error(test, exc_info=True)

    def addError(self, test, err):
        super().addError(test, err)
        if self.verbosity >= 3:
            MyLogging.getLogger().critical(test, exc_info=True)


class MyHTMLTestRunner(XTestRunner.HTMLTestRunner):
    def run(self, testlist):
        """
        Run the given test case or test suite.
        """

        print('\nXTestRunner Running tests...\n')
        print('----------------------------------------------------------------------')
        for test in self.test_iter(testlist):
            # Determine if test should be skipped
            skip = bool(self.whitelist)
            test_method = getattr(test, test._testMethodName)
            test_labels = getattr(test, '_labels', set()) | getattr(test_method, '_labels', set())
            if test_labels & self.whitelist:
                skip = False
            if test_labels & self.blacklist:
                skip = True

            if skip:
                # Test should be skipped.
                @functools.wraps(test_method)
                def skip_wrapper(*args, **kwargs):
                    raise unittest.SkipTest('label exclusion')

                skip_wrapper.__unittest_skip__ = True
                if len(self.whitelist) >= 1:
                    skip_wrapper.__unittest_skip_why__ = f'label whitelist {self.whitelist}'
                if len(self.blacklist) >= 1:
                    skip_wrapper.__unittest_skip_why__ = f'label blacklist {self.blacklist}'
                setattr(test, test._testMethodName, skip_wrapper)

        result = MyTestResult(self.verbosity, rerun=self.rerun, logger=self.logger)
        testlist(result)
        self.end_time = datetime.datetime.now()
        self.run_times += 1
        self.generate_report(testlist, result)

        print("Generating HTML reports...")
        return result


def run_case(all_case, report_path=MyConfig.TESTREPORT_DIR):
    now = time.strftime("%Y%m%d")
    filename = report_path + '/' + f"result-{now}" + '.html'
    with open(filename, 'wb') as file:
        # loguru._level = "DEBUG"
        # loguru._console_format = "{time} {level} {message}"
        # loguru._console_format = "<green>{time}</green> <level>{message}</level>"
        # runner = XTestRunner.HTMLTestRunner(stream=fp,
        runner = MyHTMLTestRunner(stream=file,
                                  verbosity=3,
                                  title='接口自动化测试报告',
                                  tester='Jason',
                                  description='环境：windows 10 浏览器：chrome',
                                  language='zh-CN',
                                  logger=None,
                                  rerun=0  # rerun: 重跑次数
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
    # if "password" in smtp_config and smtp_config["password"] != "":
    #     # send_mail(latest_file_path, smtp_config)
    #     # 使用XTestRunner发送邮件
    #     runner.send_email(
    #         user=smtp_config["user"],
    #         password=smtp_config["password"],
    #         host=smtp_config["smtp_host"],
    #         to="1759765836@qq.com",
    #         attachments=latest_file_path,
    #         ssl=True
    #     )


if __name__ == "__main__":
    MyLogging.set_root_logger_format()
    logging.info("main start...", extra={"prefix": "\n"})
    logging.getLogger().setLevel(logging.INFO)

    """加载testcase目录下所有test开头的py文件"""
    cases = unittest.defaultTestLoader.discover(MyConfig.TEST_CASE, pattern='loguru_test*.py')
    # cases = unittest.defaultTestLoader.discover(MyConfig.TEST_CASE, pattern='test*.py')
    run_case(cases)
