import logging
import re

import pytest
import pandas as pd

from utils import myutil


def load_data_from_excel() -> list:
    df = pd.read_excel(myutil.get_latest_file_path("./../testdata", ".xlsx"))  # 读取 Excel 文件
    excel_data: list = df.values.tolist()  # 将数据转换为列表
    if len(excel_data) == 0: return []
    excel_title = df.columns.tolist()
    return excel_data


@pytest.mark.parametrize("excel_data", load_data_from_excel())
def test_addition(excel_data: list):
    logging.debug(excel_data)
    assert re.search(r"lqc_[0-8]", excel_data[0]) is not None


if __name__ == '__main__':
    pytest.main()
