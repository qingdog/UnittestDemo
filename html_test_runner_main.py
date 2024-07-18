# encoding=utf-8
import logging
import os
import sys
import time
import datetime
import unittest
from jd_HTMLTestRunner import HTMLTestRunner
from jd_HTMLTestRunner.HTMLTestRunner import _TestResult

# from .HTMLTestRunner import HTMLTestRunner, _TestResult
# from unittest import TextTestResult

test_path = "testcase"
report_path = "./report/test-report" + time.strftime("%Y-%m-%d") + '.html'
report_title = "测试报告"
report_description = "测试用例详情"


class ColoredFormatter(logging.Formatter):
    def __init__(self, fmt=None, datefmt=None, style='%'):
        super().__init__(fmt, datefmt, style)

    def format(self, record):
        # 定义颜色
        color_codes = {
            logging.DEBUG: '\033[94m',  # 蓝色
            logging.INFO: '\033[92m',  # 绿色
            logging.WARNING: '\033[93m',  # 黄色
            logging.ERROR: '\033[91m',  # 红色
            logging.CRITICAL: '\033[95m'  # 紫色
        }
        # 添加颜色代码
        record.levelname = color_codes.get(record.levelno, '\033[0m') + record.levelname + '\033[0m'
        return super().format(record)


projectPath = os.path.abspath('.')
logPath = projectPath + '\\logs\\'
log_name = os.path.join(logPath, '%s.log' % (time.strftime('%Y%m%d_%H')))

# LOG日志记录
logging.basicConfig(level=logging.DEBUG,
                    format='[%(asctime)s] - [%(filename)s:%(lineno)d] %(levelname)s %(message)s',
                    datefmt='%Y-%m-%d_%H:%M:%S',
                    # stream=sys.stdout,
                    # filename='my.log',
                    # filemode='a',
                    handlers=[
                        logging.FileHandler(f"{log_name}", encoding="UTF-8", mode='a'),  # 文件日志处理器
                        logging.StreamHandler(sys.stdout)  # 控制台日志处理器
                    ]
                    )
logger = logging.getLogger()
# 获取控制台日志处理器
console_handler = logger.handlers[-1]
# 创建控制台日志格式化器（包含颜色代码）
console_handler.setFormatter(ColoredFormatter(
    fmt='[%(asctime)s] - [%(filename)s:%(lineno)d] %(levelname)s %(message)s',
    datefmt='%Y-%m-%d_%H:%M:%S'
))


# class MyTestRunner(unittest.TextTestRunner):
#     def _makeResult(self):
#         return MyTestResult(self.stream, self.descriptions, self.verbosity)


# class MyTestResult(TextTestResult):
class MyTestResult(_TestResult):
    # def __init__(self, stream, descriptions, verbosity):
    #     # 关闭流，这样就不会有任何输出到控制台
    #     # super(QuietTestResult, self).__init__(open(os.devnull, 'w'), descriptions, verbosity)
    #     # 使用传入的流，而不是关闭它
    #     super(QuietTestResult, self).__init__(stream, descriptions, verbosity)

    def addError(self, test, err):
        # 记录错误到日志文件，不在控制台输出
        logging.getLogger().error("Error in test %s", test, exc_info=err)
        super(MyTestResult, self).addError(test, err)

    def addFailure(self, test, err):
        logging.getLogger().error("Failure in test %s", test, exc_info=err)
        super(MyTestResult, self).addFailure(test, err)

    def printErrors(self):
        print("\r")
    #     # 阻止unittest断言失败输出
    #     if self.errors:
    #         logging.error(" MyErrors: ")
    #         for test, error in self.errors:
    #             logging.error("MyError in test %s", test)
    #             es = ""
    #             for e in error:
    #                 es += e
    #             logging.error(es)
    #     if self.failures:
    #         logging.error(" MyFailures: ")
    #         for test, failure in self.failures:
    #             logging.error("MyFailure in test %s", test)
    #             fs = ""
    #             for f in failure:
    #                 fs += f
    #             logging.error(fs)


class MyHTMLTestRunner(HTMLTestRunner):
    # def run(self, test):
    def run(self, test, django_db=None, caseTotal=None, sql=None):
        "Run the given test case or test suite."
        # result = _TestResult(self.verbosity)
        result = MyTestResult(self.verbosity)
        test(result)
        self.stopTime = datetime.datetime.now()
        self.generateReport(test, result)
        print(sys.stderr, '\nTime Elapsed: %s' % (self.stopTime - self.startTime))
        return result


if __name__ == '__main__':
    # 批量执行脚本 unittest.defaultTestLoader.discover
    # 读取脚本，报告路径
    myTestSuit = unittest.defaultTestLoader.discover(start_dir=test_path, pattern='test*.py')

    # 测试日志输出
    # logging.debug("这是一个debug信息")
    # logging.info("这是一个info信息")
    # logging.warning("这是一个warning信息")
    # logging.error("这是一个error信息")
    # logging.critical("这是一个critical信息")

    count = myTestSuit.countTestCases()
    logger.info(f'-----开始执行所有测试,总用例数：{myTestSuit.countTestCases()}')
    logger.info(myTestSuit)
    try:
        with open(f"./{report_path}", 'wb') as file:
            # with open(report_path, 'wb') as file:
            # HTMLTestRunner文件名.HTMLTestRunner构建函数init
            testRunner = MyHTMLTestRunner(stream=file,  # 在Python 3及以后的版本中，所有的字符串都是Unicode字符串，因此这个前缀通常可以省略
                                          title=report_title, description=report_description,
                                          verbosity=3)  # verbosity=2 表示冗长模式，将显示详细的测试执行信息。
            # testRunner = MyTestRunner()
            testRunner.run(myTestSuit)
            file.close()
        logger.info('------所有测试用例执行完毕-------')
    except Exception as e:
        logger.error(f"Framework: 加载异常：{e}", exc_info=True)
