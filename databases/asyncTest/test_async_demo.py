import logging
import unittest
from ddt import ddt, data, unpack

from databases.aiomysql_client import AioMySQLClient
from mysql_pool import MySQLPool  # 确保将MySQLPool类导入进来


@ddt
class TestDemo(unittest.IsolatedAsyncioTestCase):
    mysql_pool: MySQLPool = None
    test_cases = [
        {'title': "全国", 'level': 1, 'user': "残保金--全国"},
        {'title': "深圳", 'level': 1, 'user': "全国制造、交通、采矿、农林、建筑、金融、水利、信息传输、科学研究、商务服务"},
        {'title': "深圳2", 'level': 1, 'user': "不存在的项目名"},
        # 更多测试用例...
    ]

    is_init = False

    async def asyncSetUp(self):
        # if cls.is_init: return cls.is_init = True self.mysql_pool = MySQLPool(host='127.0.0.1', port=3306,
        # user='', password='', db='')

        self.aiomysql_client = AioMySQLClient()
        try:
            await self.aiomysql_client.connect()
            # await self.mysql_pool.init_pool()
        except Exception as e:
            print(f"Error initializing MySQLPool: {e}")
            raise

    async def asyncTearDown(self):
        # await self.mysql_pool.close()
        await self.aiomysql_client.close()

    # @classmethod
    # async def setUpClass(cls):
    #     await cls.mysql_pool.close()

    """
    def setUp(self):
        print(self.mysql_pool)
    """
    logging.getLogger().setLevel(logging.INFO)

    @data(*test_cases)
    @unpack
    async def test_unpack_go(self, title, level, user):
        """执行测试用例: {title}"""
        # 这里你可以使用self.mysql_pool来执行数据库操作
        # print(self.mysql_pool)

        # result = await self.mysql_pool.execute("SELECT * FROM qiye_declareable_project WHERE project_name=%s", user)
        result = await self.aiomysql_client.execute_query("SELECT * FROM qiye_declareable_project WHERE project_name=%s", user)
        logging.info(result)
        # 根据测试目的进行断言
        self.assertIsNotNone(result)