import asyncio
import json

import aiomysql


# import aiomysql.sa as aio_sa
# from sqlalchemy import Table, MetaData, create_engine
# pip install -i https://pypi.tuna.tsinghua.edu.cn/simple sqlalchemy
# pip install --upgrade urllib3==1.26.18
# or
# https://www.python.org/ftp/python/3.8.10/python-3.8.10-amd64.exe

# 创建一个异步引擎
# engine = await aio_sa.create_engine(host="", port=3306, user="root", password="123456", db="test", connect_timeout=10)
# conn = await aiomysql.connect(host='localhost', port=3306, user='root', password='123456',db='job')

class MySQLPoolClose:
    """异步上下文管理器 连接池使用完就释放（错误的用法）"""
    pool: aiomysql.Pool = None

    # 读取主配置文件
    with open('../../config.json', 'r') as file:
        conf = json.load(file)
        config = conf["database"]
        if conf["env"] == "test":
            # 读取测试配置文件
            with open('../../config_test.json', 'r') as f:
                config_test = json.load(f)["database"]
            # 使用测试配置文件中的值覆盖主配置文件中的空字段
            for key, value in config_test.items():
                if key not in config or not config[key]:
                    config[key] = value

    def __init__(self, host=config['host'], port=config['port'], user=config['user'], password=config['password'],
                 db=config['db']):
        self.host = host
        self.port = port
        self.user = user
        self.password = password
        self.db = db

    async def connect(self):
        self.pool = await aiomysql.create_pool(
            host=self.host,
            port=self.port,
            user=self.user,
            password=self.password,
            db=self.db,
        )

    async def __aenter__(self):
        await self.connect()
        # return self 返回 async with语句中as后面对象（即当前类的对象）
        return self

    async def __aexit__(self, exc_type, exc_val, exc_tb):
        print(exc_val)
        await self.close()
        # return True Python解释器处理async with块中发生的异常（默认异常处理）
        return True

    async def close(self):
        """每次使用完就关闭连接池 阻止win平台下的错误：RuntimeError: Event loop is closed"""
        if self.pool:
            self.pool.close()
        await self.pool.wait_closed()

    async def execute_query(self, sql, args=None):
        async with self.pool.acquire() as conn:
            # cursor: aiomysql.cursors.Cursor = await self.connection.cursor()
            # 异步的上下文管理 游标对象
            async with conn.cursor() as cursor:
                cursor: aiomysql.Cursor
                await cursor.execute(sql, args)
                result = await cursor.fetchall()
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
        async with self.pool.acquire() as conn:
            conn: aiomysql.Connection
            async with conn.cursor() as cursor:
                cursor: aiomysql.cursors.Cursor
                await cursor.execute(sql)
                # results = await cursor.fetchall()
                async for row in cursor:
                    yield row


# 使用示例
if __name__ == '__main__':
    async def query():
        # 创建MySQLClient实例
        async with MySQLPoolClose() as mysql_client:
            # 查询数据
            result: tuple = await mysql_client.select('qiye_declareable_project',
                                                      where="entity_id2 = '91441300717867103C' and report_deadline_time is not null")
            print(type(result))
            for r in result:
                print(r)
            # 插入数据
            # await mysql_client.insert('table_name', {'column1': 'value1', 'column2': 'value2'})
            # 更新数据
            # await mysql_client.update('table_name', {'column2': 'new_value'}, where='column1 = "value1"')
            # 删除数据
            # await mysql_client.delete('table_name', where='column1 = "value1"')

            ss = await mysql_client.execute_query("select count(*) from qiye_declareable_project")
            print(ss[0][0])

            async for row in mysql_client.async_for_cursor(sql="select * from qiye_declareable_project limit 2"):
                print(row)


    # 运行主函数
    asyncio.run(query())
