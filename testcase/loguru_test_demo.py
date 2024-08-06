import logging
import unittest

from ddt import ddt, data, file_data, unpack
from loguru import logger

from databases.aiomysql_client import AioMySQLClient
from utils.excel_testcase_processor import ExcelTestCaseProcessor
from x_test_runner_send_main import MyConfig


@ddt
class TestDemo(unittest.TestCase):
    # 假设这是从YAML文件中读取的测试用例数据
    test_cases = [
        {'title': "登录测试1", 'level': 1, 'user': "testuser1"},
        {'title': "登录测试2", 'level': 1, 'user': "testuser2"},
        # 更多测试用例...
    ]

    # @file_data(dvd_login_yml)  # 指定具体路径的用例，读之前需先装好 pyyarm 第三方模块
    # def test_login6666(self, title, level, user, password, code, body):  # 引用yaml用例里各标题，数量需要对得上
    @data(*test_cases)
    @unpack
    def test_unpack_go(self, title, level, user):  # unpack字典，key需要对得上
        """test_go={title}"""
        # self._testMethodName.__doc__ = title

    @data(*test_cases)
    def test_go(self, title):
        """test_go={0}"""

    excel_data: list[dict[str, int | str]] = ExcelTestCaseProcessor(MyConfig.TESTDATA_FILE).read_data()
    testcase_titles = []
    for row in excel_data:
        testcase_titles.append(list(row.values())[1])

    @data(*zip(testcase_titles, excel_data))
    @unpack
    def test_zip(self, name, excel_data2):
        """test_zip={0}"""
        logging.warning(name)
        logging.warning(excel_data2)

    @data(*zip(["验证码测试", "登录接口测试"], excel_data))
    @unpack
    def test_add_explain(self, title, excel_data2):
        """explain{0}"""
        # 使用title来格式化文档字符串
        # self.__doc__ = self.__doc__.format(excel_data2)

    @file_data("../testdata/dvd_login.yml")  # 指定具体路径的用例，读之前需先装好 pyyarm 第三方模块
    def test_file_data(self, title, level, user, password, code, body):
        """报告用例注释无效={0}"""
        # print(title)
        if level == "H":
            self._testMethodDoc = title
            # AioMySQLClient.run(self.query23)
        else:
            AioMySQLClient.run(self.main)

    @logger.catch(reraise=True)
    def test_catch_exception(self):
        """@logger.catch(reraise=True)捕获异常"""

        return 1 / 0

    async def main(self):
        aiomysql_client = await AioMySQLClient.get_instance()
        try:
            result = await aiomysql_client.select('qiye_declareable_project',
                                                  where="entity_id = '191441300717867103C' and report_deadline_time is not null")
            for r in result:
                print(r)
            return result
        except Exception as e:
            self.fail(e)
        finally:
            i = 1
            aiomysql_client.close()

    # @logger.catch(reraise=True)
    async def query2(self):
        aiomysql_client = await AioMySQLClient().connect()
        result: tuple = await aiomysql_client.select('qiye_declareable_project',
                                                     where="entity_id = '11441300717867103C' and report_deadline_time is not null")
        if len(result) == 0:
            self.fail("没有查到可申报项目！")
        return result

    # @logger.catch(reraise=True)
    async def query23(self):
        aiomysql_client = await AioMySQLClient().connect()
        result: tuple = await aiomysql_client.select('qiye_declareable_project',
                                                     where="entity_id = '91441300717867103C' and report_deadline_time is not null")
        return result
