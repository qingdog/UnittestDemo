import datetime
import functools
import logging
import re

import XTestRunner
from XTestRunner.htmlrunner.result import _TestResult
from loguru import logger
import os
import sys
import time
import unittest

from XTestRunner import HTMLTestRunner

from logs.mylogging import MyLogging
from utils import myutil
from utils.myutil import get_latest_file_path


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


def run_case(all_case, report_path=MyConfig.TESTREPORT_DIR):
    now = time.strftime("%Y%m%d")
    filename = report_path + '/' + f"result-{now}" + '.html'
    with open(filename, 'wb') as file:
        # loguru._level = "DEBUG"
        # loguru._console_format = "{time} {level} {message}"
        # loguru._console_format = "<green>{time}</green> <level>{message}</level>"
        # runner = XTestRunner.HTMLTestRunner(stream=fp,
        runner = HTMLTestRunner(stream=file,
                                verbosity=3,
                                title='接口自动化测试报告',
                                tester=' ',
                                description='环境：windows 10 浏览器：chrome',
                                language='zh-CN',
                                logger=None,
                                rerun=0  # rerun: 重跑次数
                                )

        runner.run(all_case)

    # 最新测试报告文件的路径
    latest_file_path = get_latest_file_path(MyConfig.TESTREPORT_DIR)
    logger.info("报告路径：" + latest_file_path)

    # try:
    #     func(5, c)
    # except ZeroDivisionError:
    #     logger.exception("What?!")


if __name__ == '__main__':
    logger2 = logging.getLogger()
    logging.getLogger().setLevel(logging.CRITICAL)
    print(logger2)
    for handler in logging.getLogger().handlers:
        handler: logging
        if not handler.get_name():
            logging.getLogger().removeHandler(handler)

    # 移除默认的日志处理器
    logger.remove()
    logger.add(sys.stdout, colorize=True, level="DEBUG", backtrace=False, diagnose=True,
               format="<green>{time:YYYY-MM-dd HH:mm:ss}</green> - <cyan>{file}:{line} {function}</cyan> "
                      "<level>{level} {message} </level>")
    logger.add(os.path.join(myutil.get_project_path(), "logs", "info_{time:YYYYMM}.log"),
               level="INFO", rotation="100 MB", retention="1 month", backtrace=False, diagnose=True)
    # 需要在test开头的py文件的test方法中加上装饰器配合使用
    cases = unittest.defaultTestLoader.discover(MyConfig.TEST_CASE, pattern='loguru_test*.py')
    run_case(cases)
