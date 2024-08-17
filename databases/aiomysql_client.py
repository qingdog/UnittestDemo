import asyncio
import json
import os
import platform
from collections import namedtuple
from typing import Callable, Coroutine, Any, Awaitable

import aiomysql

from databases.qiye_base_business import QiyeBaseBusiness
from logs.mylogging import MyLogging
from utils import myutil


class AioMySQLClient:
    _instance = None
    pool: aiomysql.Pool = None
    _lock = asyncio.Lock()

    @classmethod
    async def get_instance(cls):
        if cls._instance is None:
            async with cls._lock:
                if cls._instance is None:
                    cls._instance = cls()
                    await cls._instance.connect()
        return cls._instance

    # 读取主配置文件
    @staticmethod
    def load_config():
        with open(os.path.join(myutil.get_project_path(), './config.json'), 'r') as file:
            conf = json.load(file)
            config = conf["database"]
            if conf["env"] == "test":
                # 读取测试配置文件
                with open(os.path.join(myutil.get_project_path(), './config_test.json'), 'r') as f:
                    config_test = json.load(f)["database"]
                # 使用测试配置文件中的值覆盖主配置文件中的空字段
                for key, value in config_test.items():
                    if key not in config or not config[key]:
                        config[key] = value
        return config

    config = load_config()

    # def __init__(self):
    #     self.config = self.load_config()

    async def connect(self, host=config['host'], port=config['port'], user=config['user'], password=config['password'],
                      db=config['db'], loop=None):
        # MyLogging.getLogger("database").info("database connecting...")
        self.pool = await aiomysql.create_pool(
            host=host,
            port=port,
            user=user,
            password=password,
            db=db,
            loop=loop
        )
        return self

    async def close(self):
        if self.pool:
            self.pool.close()
            await self.pool.wait_closed()

    async def execute_query(self, sql, args=None):
        if self.pool is None:
            await self.connect()
        async with self.pool.acquire() as conn:
            # cursor: aiomysql.cursors.Cursor = await self.connection.cursor()
            # 异步的上下文管理 游标对象
            async with conn.cursor(aiomysql.DictCursor) as cursor:
                cursor: aiomysql.Cursor
                await cursor.execute(sql, args)
                result: tuple = await cursor.fetchall()

                return result

    async def select(self, table, columns='*', where=None, order_by=None, limit=None):
        query = f"SELECT {columns} FROM {table}"
        if where:
            query += f" WHERE {where}"
        if order_by:
            query += f" ORDER BY {order_by}"
        if limit:
            query += f" LIMIT {limit}"
        return await self.execute_query(query)

    async def insert(self, table, data):
        placeholders = ', '.join(['%s'] * len(data))
        columns = ', '.join(data.keys())
        values = tuple(data.values())
        query = f"INSERT INTO {table} ({columns}) VALUES ({placeholders})"
        return await self.execute_query(query, values)

    async def update(self, table, data, where):
        updates = ', '.join([f"{key} = %s" for key in data.keys()])
        values = tuple(data.values())
        query = f"UPDATE {table} SET {updates} WHERE {where}"
        return await self.execute_query(query, values)

    async def delete(self, table, where):
        query = f"DELETE FROM {table} WHERE {where}"
        return await self.execute_query(query)

    async def async_for_cursor(self, sql):
        """游标迭代，拉取一小部分数据（通常是内部缓冲区大小的数据），逐行返回"""
        async with self.pool.acquire() as conn:
            conn: aiomysql.Connection
            async with conn.cursor(aiomysql.DictCursor) as cursor:
                cursor: aiomysql.cursors.Cursor
                await cursor.execute(sql)
                # results = await cursor.fetchall()
                async for row in cursor:
                    yield row

    async def fetchmany_until_over(self, sql, *args, size=100):
        """分批次获取结果，一次获取100条记录直到为空"""
        async with self.pool.acquire() as conn:
            # 游标结果返回字典格式
            async with conn.cursor(aiomysql.DictCursor) as cur:
                cur: aiomysql.cursors.Cursor
                await cur.execute(sql, args)
                while True:
                    results = await cur.fetchmany(size=size)
                    if not results:
                        break
                    yield results

    new_event_loop = asyncio.new_event_loop()
    asyncio.set_event_loop(new_event_loop)

    @classmethod
    def run(cls, main: Callable[[], Coroutine[Any, Any, tuple]]):
        """执行异步函数"""
        # 处理win平台 asyncio.run() 执行完所产生的异常
        if platform.system() == 'Windows':
            async def win_shutdown_default_executor():
                await asyncio.BaseEventLoop.shutdown_default_executor()
                await asyncio.sleep(0.25)
                # await asyncio.sleep(3)

            asyncio.BaseEventLoop.originalShutdownFunc = win_shutdown_default_executor
            # asyncio.BaseEventLoop.set_exception_handler(self=cls.new_event_loop, handler=win_shutdown_default_executor)

        _is_use_old_api = False
        if _is_use_old_api:
            cls.new_event_loop.run_until_complete(main())
        else:
            # 运行主函数
            asyncio.run(main())


async def main():
    aiomysql_client = await AioMySQLClient.get_instance()
    try:
        result = await aiomysql_client.select('qiye_declareable_project',
                                              where="entity_id = '191441300717867103C' and report_deadline_time is not null")
        for r in result:
            print(r)
        return result
    except Exception as e:
        raise RuntimeError(e)
        # self.fail(e)
    finally:
        aiomysql_client.close()


# 使用示例
if __name__ == '__main__':
    asyncio.run(main())


    async def query():
        aiomysql_client = await AioMySQLClient().connect()
        # result: tuple = await aiomysql_client.select('qiye_declareable_project', where="entity_id =
        # '91441300717867103C' and report_deadline_time is not null")

        # 创建MySQLClient实例
        # aiomysql_client = await AioMySQLClient.get_instance()
        # await AioMySQLClient().connect()

        # 查询数据
        result: tuple = await aiomysql_client.select('qiye_declareable_project',
                                                     where="entity_id = '91441300717867103C' and report_deadline_time is not null")
        print(type(result))
        for r in result:
            print(r)
        # 插入数据
        # await mysql_client.insert('table_name', {'column1': 'value1', 'column2': 'value2'})
        # 更新数据
        # await mysql_client.update('table_name', {'column2': 'new_value'}, where='column1 = "value1"')
        # 删除数据
        # await mysql_client.delete('table_name', where='column1 = "value1"')

        mysql_client = aiomysql_client
        """mysql_client = await AioMySQLClient.get_instance()
        print(id(mysql_client))"""

        result_business = await mysql_client.execute_query("select * from qiye_base_business limit 10")
        print(result_business[0]["company"])

        qiye_base_businesses = [QiyeBaseBusiness(*row.values()) for row in result_business]
        for business in qiye_base_businesses:
            print(business.company)

        async for row in mysql_client.async_for_cursor(sql="select * from qiye_declareable_project limit 2"):
            print(row)

        # query = "select * from qiye_base_business limit 200"
        # #async for row in mysql_client.fetchmany_until_over(query, 'zhang', '23'):
        # async for rows in mysql_client.fetchmany_until_over(query):
        #     rows: list[dict]
        #     for bus in rows:
        #         bu = QiyeBaseBusiness(*bus.values())
        #         print(bu.id)


    # async def querys:
    #     并发执行两个查询
    #     result = await asyncio.gather(query1(), query2())
    #     for i in result:
    #         print(i)
    # AioMySQLClient.run(main=querys)

    AioMySQLClient.run(main=query)
