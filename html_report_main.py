# encoding=utf-8
import logging
import os
import sys
import time
import unittest
import HTMLReport
from logs.mylogging import MyLogging


from BeautifulReport import BeautifulReport

test_path = "testcase"
str_time = time.strftime("%Y-%m-%d")
report_path = "reports"
report_name = f"{str_time}"
report_title = "测试报告"
report_description = "测试用例详情"

project_path = os.path.abspath('.')


class MyBeautifulReport(BeautifulReport):
    logger = logging.getLogger()

    def addFailure(self, test, err):
        # 重写 unittest.TestResult 的 addFailure 方法打印和记录日志
        self.logger.error(test, exc_info=True)
        super().addFailure(test, err)

    def addError(self, test, err):
        self.logger.error(test, exc_info=True)
        super().addFailure(test, err)


if __name__ == '__main__':
    # 批量执行脚本 unittest.defaultTestLoader.discover
    # 读取脚本，报告路径
    myTestSuit = unittest.defaultTestLoader.discover(start_dir=test_path, pattern='test*.py')

    # 让unittest框架按照用例方法编写的顺序来执行
    # my_loader = MyTestLoader()
    # myTestSuit = my_loader.discover(start_dir=test_path, pattern='test*.py'

    count = myTestSuit.countTestCases()
    logger = MyLogging.getLogger()
    # logger = logging.getLogger()

    logger.info(f'-----开始执行所有测试,总用例数：{myTestSuit.countTestCases()}')
    logger.info(myTestSuit)
    try:
        # HTMLReport移除了已有的根处理器
        test_runner = HTMLReport.TestRunner(
            report_file_name=report_name,
            log_file_name="./logs",
            output_path=report_path,
            title=None,
            description=None,
            thread_count=1,  # 1线程
            thread_start_wait=0,
            tries=0,
            delay=0,
            back_off=1,
            retry=True,
            sequential_execution=True,  # 按照套件添加(addTests)顺序执行
            lang="cn"
        )

        # test_suite = unittest.defaultTestLoader.discover('./tests', pattern='test*.py')
        test_runner.run(myTestSuit)
        logger.info('------所有测试用例执行完毕-------')
    except Exception as e:
        logger.error(f"异常：{e}", exc_info=True)
