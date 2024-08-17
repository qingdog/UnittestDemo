import asyncio
import unittest
from ddt import ddt, data, unpack
from mysql_pool import MySQLPool  # 确保将MySQLPool类导入进来


@ddt
class TestDemo(unittest.IsolatedAsyncioTestCase):
    mysql_pool = None
    test_cases = [
        {'title': "登录测试1", 'level': 1, 'user': "testuser1"},
        {'title': "登录测试2", 'level': 1, 'user': "testuser2"},
        # 更多测试用例...
    ]

    @classmethod
    async def asyncSetUpClass(cls):
        cls.mysql_pool = MySQLPool(host='127.0.0.1', port=3306, user='root', password='', db='mysql')
        await cls.mysql_pool.init_pool()

    @classmethod
    async def asyncTearDownClass(cls):
        await cls.mysql_pool.close()

    @data(*test_cases)
    @unpack
    async def test_unpack_go(self, title, level, user):
        """执行测试用例: {title}"""
        # 这里你可以使用self.mysql_pool来执行数据库操作
        result = await self.mysql_pool.execute("SELECT * FROM users WHERE username=%s", user)
        # 根据测试目的进行断言
        self.assertIsNotNone(result)

    @data(*test_cases)
    async def test_go(self, title):
        """执行测试用例: {0}"""
        # 这里你可以使用self.mysql_pool来执行数据库操作
        # 例如：检查用户是否存在
        user = self.test_cases[0]['user']  # 假设我们使用第一个测试用例的用户
        result = await self.mysql_pool.execute("SELECT * FROM users WHERE username=%s", user)
        # 根据测试目的进行断言
        self.assertIsNotNone(result)


if __name__ == '__main__':
    unittest.main()
