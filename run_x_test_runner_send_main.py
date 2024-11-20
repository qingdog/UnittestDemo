#!/usr/bin/env python
# _*_ coding:utf-8 _*_
__author__ = 'YinJia'

import configparser
from datetime import datetime, timedelta
import functools
import logging
import os
import re
import sys
import time
import unittest

import XTestRunner
import requests
from XTestRunner import HTMLTestRunner, Weinxin
from XTestRunner.htmlrunner.result import _TestResult
from dotenv import load_dotenv

from logs.mylogging import MyLogging, ColoredFormatter
from utils import myutil
from utils.myutil import get_latest_file_path


class MyConfig:
    FILE_DIR = os.path.dirname(__file__)
    sys.path.append(FILE_DIR)

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
    TESTDATA_FILE = os.path.join(TESTDATA_DIR if xlsx_files else FILE_DIR, xlsx_files[-1])


class MyTestResult(_TestResult):
    def addFailure(self, test, err):
        super().addFailure(test, err)
        if self.verbosity >= 3:
            # 用例执行失败后，使用 `严重错误` 级别的日志输出
            MyLogging.getLogger().critical(test, exc_info=True)

    def addError(self, test, err):
        super().addError(test, err)
        if self.verbosity >= 3:
            MyLogging.getLogger().error(test, exc_info=True)


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
        self.end_time = datetime.now()
        self.run_times += 1
        self.generate_report(testlist, result)

        print("Generating HTML reports...")
        return result


def run_case(all_case, report_path=MyConfig.TESTREPORT_DIR):
    now = time.strftime("%Y%m%d")
    filename = report_path + '/' + f"result-{now}" + '.html'
    log_latest_file_path = get_latest_file_path(os.path.join(MyConfig.FILE_DIR, "logs"))

    with open(filename, 'wb') as file:
        # loguru._level = "DEBUG"
        # loguru._console_format = "{time} {level} {message}"
        # loguru._console_format = "<green>{time}</green> <level>{message}</level>"
        # runner = XTestRunner.HTMLTestRunner(stream=fp,
        # testcase_url = '测试用例：<a href="https://kdocs.cn/l/coyHI6Y1g5Xr">https://kdocs.cn/l/coyHI6Y1g5Xr</a>'
        testcase_url = '测试'
        runner = MyHTMLTestRunner(stream=file,
                                  verbosity=3,
                                  title='接口测试报告',
                                  tester=testcase_url,
                                  description=f'日志：<a href="/logs/{now}.log">/logs/{now}.log</a>',
                                  language='zh-CN',
                                  logger=None,
                                  rerun=0  # rerun: 重跑次数
                                  )

        runner.run(all_case)

    # 最新测试报告文件的路径
    latest_file_path = get_latest_file_path(MyConfig.TESTREPORT_DIR)
    logging.getLogger().info("报告路径：" + latest_file_path)

    # 修改html文件用于展开所有用例
    re_line = "(.*<script language=\"javascript\".*)"
    re_new_line = "\\1 ;;showCase(5, 1);"
    myutil.html_line_to_new_line(latest_file_path, "utf-8", re_line, re_new_line)

    # return  # 不发送邮件
    # mail_util.send_mail(latest_file_path, smtp_config)
    logging.info(f"XTestRunner发送邮件到 {os.getenv("smtp_email_recipient")}")
    if os.getenv("smtp_email_recipient"):
        runner.send_email(
            to=os.getenv("smtp_email_recipient"),
            user=os.getenv("smtp_user"),
            password=os.getenv("smtp_password"),
            host=os.getenv("smtp_host"),
            port=os.getenv("smtp_port"),
            attachments=latest_file_path,
            ssl=True
        )

    def send_wx_notify(self, send=False):
        if send:
            report = "./reports/result-20240823.html"
            with open(report, 'wb') as fp:
                runner = HTMLTestRunner(
                    stream=fp,
                    title='测试发送到企业微信',
                    tester='huang',
                    description=['类型：发送测试消息'],
                    language="zh-CN"
                )
                # runner.run(suit)
                # 方式一： send_weixin() 方法
                runner.send_weixin(
                    access_token="a-b-c-d-e",
                    at_mobiles=[12345678901],
                    is_at_all=False,
                )


class EnterpriseWeiXin(Weinxin):
    # https://developer.work.weixin.qq.com/document/path/91770#文件上传接口
    def upload_file_to_wechat(self, key, file_path, file_type='file'):
        """
        上传文件到企业微信机器人，并获取media_id。(未测试)

        :param key: 调用接口凭证，机器人webhookurl中的key参数
        :param file_path: 要上传的文件的路径
        :param file_type: 文件类型，默认为'file'，可选'voice'
        :return: 响应内容，包含media_id
        """
        url = f"https://qyapi.weixin.qq.com/cgi-bin/webhook/upload_media?key={key}&type={file_type}"
        # 读取文件内容
        with open(file_path, 'rb') as f:
            file_content = f.read()

        # 获取文件名
        file_name = file_path.split('/')[-1]

        # 设置请求头
        headers = {
            'Content-Type': 'multipart/form-data; boundary=----WebKitFormBoundary7MA4YWxkTrZu0gW'
        }

        # 构造请求体
        payload = (
            f'------WebKitFormBoundary7MA4YWxkTrZu0gW\r\n'
            f'Content-Disposition: form-data; name="media"; filename="{file_name}"\r\n'
            f'Content-Type: application/octet-stream\r\n\r\n'
            f'{file_content}\r\n'
            '------WebKitFormBoundary7MA4YWxkTrZu0gW--'
        )

        # 发送请求
        response = requests.post(url, headers=headers, data=payload)
        res = response.json()
        if res.get('errcode') != 0:
            return None
        return res.get('media_id')

    def send_upload_file(self, media_id: str = None):
        """
        发送 文件类型
        :param media_id : 文件id，通过企业微信的文件上传接口获取
        :return:
        """

        message = {
            "msgtype": "file",
            "file": {
                "media_id": f"{media_id}"
            }
        }
        resp = self._send_message(self.url, message)
        if resp["errcode"] != 0:
            logging.error("❌ weixin failed to send!!")
            logging.error(resp)
        return resp


if __name__ == "__main__":
    MyLogging.set_root_logger_format()
    load_dotenv()
    logging.info("main start...", extra={"prefix": "\n"})
    logging.getLogger().setLevel(logging.INFO)

    """加载testcase目录下所有test开头的py文件"""
    # cases = unittest.defaultTestLoader.discover(MyConfig.TEST_CASE, pattern='loguru_test*.py')
    cases = unittest.defaultTestLoader.discover(MyConfig.TEST_CASE, pattern='test_api*.py')
    run_case(cases)
