import asyncio
import json
import logging
import os
import platform
from collections import namedtuple
from collections.abc import AsyncGenerator
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

    async def execute_query(self, sql, *args):

        if self.pool is None:
            await self.connect()
        async with self.pool.acquire() as conn:
            # cursor: aiomysql.cursors.Cursor = await self.connection.cursor()
            # 异步的上下文管理 游标对象
            async with conn.cursor(aiomysql.DictCursor) as cursor:
                cursor: aiomysql.Cursor
                self.show_sql_log(sql, *args)
                await cursor.execute(sql, args)
                result: tuple = await cursor.fetchall()

                return result

    def show_sql_log(self, sql, *args, level=logging.DEBUG):
        # 注意：这里仅适用于字符串参数，这仅用于日志记录，不应用于实际的数据库查询
        if args is not None:
            if isinstance(args, (list, tuple)):
                # 对于列表或元组，我们假设SQL语句中的占位符与args的元素一一对应
                # 注意：这仅用于日志记录，不应用于实际的数据库查询
                formatted_sql = sql % tuple(repr(arg) for arg in args)
            elif isinstance(args, dict):
                # 对于字典，我们假设SQL语句中的占位符是字典的键
                formatted_sql = sql.format(**{k: repr(v) for k, v in args.items()})
            else:
                # 对于单个参数，直接替换
                formatted_sql = sql % repr(args)
        else:
            formatted_sql = sql

        # 将格式化后的SQL输出到日志
        if level == logging.DEBUG:
            logging.debug(f"【SQL】: {formatted_sql}")
        else:
            logging.info(f"【SQL】: {formatted_sql}")

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
    def run(cls, run_main, *args, is_old_run=True):
        """执行异步函数"""
        if is_old_run:
            cls.new_event_loop.run_until_complete(run_main(*args))
        else:
            # 处理win平台 asyncio.run() 执行完所产生的异常
            if platform.system() == 'Windows':
                async def win_shutdown_default_executor():
                    await asyncio.BaseEventLoop.shutdown_default_executor()
                    await asyncio.sleep(0.25)
                    # await asyncio.sleep(3)

                asyncio.BaseEventLoop.originalShutdownFunc = win_shutdown_default_executor
                # asyncio.BaseEventLoop.set_exception_handler(self=cls.new_event_loop, handler=win_shutdown_default_executor)
            # 运行主函数
            asyncio.run(run_main(*args))


async def main():
    aiomysql_client = await AioMySQLClient.get_instance()
    try:
        result = await aiomysql_client.select('qiye_declareable_project',
                                              where="entity_id = '191441300717867103C' and report_deadline_time is not null")
        for r in result:
            print(r)

    except Exception as e:
        raise RuntimeError(e)
        # self.fail(e)
    finally:
        await aiomysql_client.close()
    return result


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

        return result

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

    AioMySQLClient.run(run_main=query)
