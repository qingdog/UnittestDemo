# encoding=utf-8
import logging
import os
import time

from BeautifulReport import BeautifulReport
from utils.order_test_loader import OrderTestLoader
from utils import color_format_logging
import utils.myutil

test_path = "testcase"
str_time = time.strftime("%Y-%m-%d_%H")
report_path = "reports"
report_name = f"test-report_{str_time}"
report_title = "测试报告"
report_description = "测试用例详情"

project_path = os.path.abspath('.')

color_format_logging.main()
logger = logging.getLogger()


class MyBeautifulReport(BeautifulReport):
    def addFailure(self, test, err):
        # 重写 unittest.TestResult 的 addFailure 方法打印和记录日志
        logger.error(test, exc_info=True)
        super().addFailure(test, err)

    def addError(self, test, err):
        logger.error(test, exc_info=True)
        super().addFailure(test, err)


def main():
    # 批量执行脚本
    # myTestSuit = unittest.defaultTestLoader.discover(start_dir=test_path, pattern='test*.py')

    # 使用自定义的加载器来执行用例
    my_loader = OrderTestLoader()
    my_test_suite = my_loader.discover(start_dir=test_path, pattern='test*.py')

    logger.info(f'-----开始执行所有测试,总用例数：{my_test_suite.countTestCases()}')
    logger.info(my_test_suite)
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
        beautiful_report = MyBeautifulReport(my_test_suite)
        beautiful_report.verbosity = 2
        beautiful_report.report(description=f'{report_description}: {os.path.join(project_path, test_path, "test_api*.py")}',
                                filename=f'{report_name}',
                                report_dir=f'{report_path}', theme='theme_default')

        logger.info('------所有测试用例执行完毕-------')

        # 最新测试报告文件的路径
        latest_file_path = utils.myutil.get_latest_file_path(report_path)
        utils.myutil.html_cdn_to_static(latest_file_path, "utf-8")
    except Exception as e:
        logger.error(f"异常：{e}", exc_info=True)


if __name__ == '__main__':
    main()
