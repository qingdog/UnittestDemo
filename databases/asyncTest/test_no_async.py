import logging
import unittest
from ddt import ddt, data, unpack

from databases.aiomysql_client import AioMySQLClient
from mysql_pool import MySQLPool  # 确保将MySQLPool类导入进来


@ddt
class TestNoAsync(unittest.TestCase):
    mysql_pool: MySQLPool = None
    test_cases = [
        {'title': "全国", 'level': 1, 'user': "残保金--全国"},
        {'title': "深圳2", 'level': 1, 'user': "不存在的项目名"},
        # 更多测试用例...
    ]

    # @data(*test_cases)
    # @unpack
    # async def test_unpack_go2(self, title, level, user):
    #     """执行测试用例: {title}"""
    #
    #     async def query2():
    #         aiomysql_client = await AioMySQLClient.connect()
    #         result: tuple = await aiomysql_client.execute_query("SELECT * FROM qiye_declareable_project WHERE "
    #                                                             "project_name=%s limit 2", user)
    #         return result
    #
    #     AioMySQLClient.run(query2)
    #     # 根据测试目的进行断言
    #     # self.assertIsNotNone(title)

    aiomysql_client: AioMySQLClient = None

    @data(*test_cases)
    @unpack
    def test_dd(self, title, level, user):
        async def query():
            self.aiomysql_client = await AioMySQLClient().get_instance()
            result: tuple = await self.aiomysql_client.execute_query("SELECT * FROM qiye_declareable_project WHERE "
                                                                     "project_name=%s limit 2", user)

            print(result)

        AioMySQLClient.run(run_main=query)
