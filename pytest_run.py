import glob
import logging
import os
import re
import sys

import pytest
from dotenv import load_dotenv

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
    # 首先尝试在TESTDATA_DIR中查找.xlsx文件
    # xlsx_files = [file for file in os.listdir(TESTDATA_DIR) if re.search("\\.xlsx?$", file)]
    xlsx_file = get_latest_file_path(".", ".xlsx")
    TESTDATA_FILE = os.path.join(FILE_DIR, xlsx_file) if xlsx_file else None


def main():
    # unittest.main()  使用pytest执行测试
    load_dotenv()
    import utils.color_format_logging

    utils.color_format_logging.main()

    logging.getLogger().setLevel(logging.INFO)
    logging.info("main start...", extra={"prefix": "\n"})
    """加载testcase目录下所有test开头的py文件"""

    log_format = "[%(asctime)s]-[%(filename)s:%(lineno)d]-[%(levelname)s]%(message)s"
    script = f'pytest {MyConfig.TEST_CASE} --alluredir={MyConfig.TESTREPORT_DIR}/test-results --log-date-format=%Y-%m-%d_%H:%M:%S --log-format={log_format} --color=yes -vs --log-cli-level=info'
    script = re.sub(r"^pytest.+?--", "--", script)  # 删除执行目录，使用glob.glob匹配测试脚本
    pytest.main(glob.glob(f'{MyConfig.TEST_CASE}/test_api*.py') + script.split(" "))
    os.system(f"allure generate {MyConfig.TESTREPORT_DIR}/test-results -o {MyConfig.TESTREPORT_DIR}/allure-report --clean")

    # 最新测试报告文件的路径
    latest_file_path = get_latest_file_path(MyConfig.TESTREPORT_DIR, suffix=".html")
    logging.getLogger().info("报告路径：" + latest_file_path)


if __name__ == "__main__":
    main()
