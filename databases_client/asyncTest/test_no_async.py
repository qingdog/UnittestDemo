import logging
import unittest
from ddt import ddt, data, unpack

from databases.aiomysql_client import AioMySQLClient
from mysql_pool import MySQLPool  # 确保将MySQLPool类导入进来


@ddt
class TestNoAsync(unittest.TestCase):
    mysql_pool: MySQLPool = None
    test_cases = [
        {'title': "全国", 'level': 1, 'name': "残保金--全国"},
        {'title': "深圳", 'level': 1, 'name': "不存在的项目名"},
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
    def test_dd(self, title, level, name):
        self.query_by_key(title, name)

    async def query(self, *arg):
        self.aiomysql_client = AioMySQLClient()
        query_result: tuple = await self.aiomysql_client.execute(
            "SELECT * FROM qiye_declareable_project WHERE project_name=%s limit 2", *arg)
        self.assertIsNot(len(query_result), 0)

        logging.info(query_result)

    def query_by_key(self, key, *args):
        keys = ["全国", "深圳"]
        # 使用示例
        handler = self.QueryHandler()
        handler.dispatch(f'key{keys.index(key)}', *args)  # 输出: 处理键1的方法
        # handler.dispatch('key2')  # 输出: 处理键2的方法
        # handler.dispatch('key4')  # 输出: 默认处理方法，因为没有定义handle_key4

    class QueryHandler:
        def handle_key0(self, *args):
            AioMySQLClient.run(TestNoAsync().query, *args)

        def handle_key1(self, *args):
            print("处理键1的方法")

        def handle_key2(self, *args):
            print("处理键2的方法")

        def handle_default(self, *args):
            print("策略模式 默认方法")

        def dispatch(self, key, *args):
            method_name = 'handle_' + str(key)
            method = getattr(self, method_name, self.handle_default)
            method(*args)