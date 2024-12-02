# encoding=utf-8
import logging
import os
import time

import unittest
from BeautifulReport import BeautifulReport

test_path = "testcase"
str_time = time.strftime("%Y-%m-%d_%H")
report_path = "reports"
report_name = f"test-report_{str_time}"
report_title = "测试报告"
report_description = "测试用例详情"

project_path = os.path.abspath('.')

import utils.color_format_logging
logger = logging.getLogger()


class MyBeautifulReport(BeautifulReport):
    def addFailure(self, test, err):
        # 重写 unittest.TestResult 的 addFailure 方法打印和记录日志
        logger.error(test, exc_info=True)
        super().addFailure(test, err)

    def addError(self, test, err):
        logger.error(test, exc_info=True)
        super().addFailure(test, err)


if __name__ == '__main__':
    # 批量执行脚本 unittest.defaultTestLoader.discover
    # 读取脚本，报告路径
    myTestSuit = unittest.defaultTestLoader.discover(start_dir=test_path, pattern='test*.py')

    # 让unittest框架按照用例方法编写的顺序来执行
    # my_loader = MyTestLoader()
    # myTestSuit = my_loader.discover(start_dir=test_path, pattern='test*.py')

    count = myTestSuit.countTestCases()
    logger.info(f'-----开始执行所有测试,总用例数：{myTestSuit.countTestCases()}')
    logger.info(myTestSuit)
    try:
        # with open(f"./{report_path}", 'w', encoding='UTF-8') as file:
        #     # with open(report_path, 'wb') as file:
        #     # HTMLTestRunner文件名.HTMLTestRunner构建函数init
        #     testRunner = HTMLTestRunner(stream=file,  # 在Python 3及以后的版本中，所有的字符串都是Unicode字符串，因此这个前缀通常可以省略
        #                                 title=report_title, description=report_description,
        #                                 verbosity=3)  # verbosity=2 表示冗长模式，将显示详细的测试执行信息。
        #     testRunner.run(myTestSuit)
        # file.close()

        # test_suite = unittest.defaultTestLoader.discover('./tests', pattern='test*.py')
        beautifulReport = MyBeautifulReport(myTestSuit)
        beautifulReport.verbosity = 2
        beautifulReport.report(description=f'{report_description}: {os.path.join(project_path, test_path, "test_api*.py")}',
                               filename=f'{report_name}',
                               report_dir=f'{report_path}', theme='theme_default')
        logger.info('------所有测试用例执行完毕-------')
    except Exception as e:
        logger.error(f"异常：{e}", exc_info=True)
