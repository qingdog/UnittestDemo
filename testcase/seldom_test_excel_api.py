import unittest
import ddt
from seldom import data

from utils.excel_testcase_processor import ExcelTestCaseProcessor
# from utils.xlrd_excel import XlrdExcel
from run_x_test_runner_send_main import MyConfig


@ddt.ddt
class SeldomTestAPI(unittest.TestCase):
    # testData: list[dict[str, int]] = XlrdExcel(MyConfig.TESTDATA_FILE).read_data()

    excel_data: list[dict[str, int | str]] = ExcelTestCaseProcessor(MyConfig.TESTDATA_FILE).read_data()
    names = []
    for row in excel_data:
        names.append(list(row.values())[1])

    # https://seldomqa.github.io/getting-started/data_driver.html#data-方法
    # @ddt.data(*ExcelTestCaseProcessor(MyConfig.TESTDATA_FILE).read_data())
    # @data(list(zip(names, excel_data)))
    @data(list(zip(names, excel_data)))
    def test_api(self, name, excel_data: dict):
        """描述："""
        # html报告日志
        print(excel_data)


if __name__ == '__main__':
    unittest.main()
