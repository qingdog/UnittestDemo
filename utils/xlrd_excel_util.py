#!/usr/bin/env python
# _*_ coding:utf-8 _*_
__author__ = 'YinJia'

import xlrd


class XlrdExcel:
    """读取excel文件数据"""

    def __init__(self, filename):
        self.workbook = xlrd.open_workbook(filename)

    def read_all_sheets_data(self):
        sheet_names = self.workbook.sheet_names()  # 获取所有sheet的名称
        all_sheets_data = {}
        for sheet_name in sheet_names:
            testcase_list = self.read_data(sheet_name=sheet_name)
            all_sheets_data[sheet_name] = testcase_list
        return all_sheets_data

    def read_data(self, sheet_name="Sheet1"):
        sheet = self.workbook.sheet_by_name(sheet_name)
        # 获取总行数、总列数
        nrows = sheet.nrows
        ncols = sheet.ncols
        if nrows > 1:
            # 获取第一行的内容，列表格式
            keys = sheet.row_values(0)
            testcase_list = []
            # 获取每一行的内容，列表格式
            for row in range(1, nrows):
                values = sheet.row_values(row)
                # keys，values组合转换为字典
                testcase_dict = dict(zip(keys, values))
                # 在字典中添加行号，行号从1开始
                testcase_dict['row_number'] = row + 1  # 行号通常是从1开始的，所以加1
                testcase_list.append(testcase_dict)
            return testcase_list
        else:
            print("表格是空数据!")
            return None
