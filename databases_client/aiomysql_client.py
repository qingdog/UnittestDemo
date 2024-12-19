import asyncio
import logging
import os
import aiomysql
from dotenv import load_dotenv


class AioMySQLClient:
    load_dotenv()
    pool: aiomysql.Pool = None

    def __init__(self, host: str = None, port: int = None, user: str = None, password: str = None, db: str = None, loop=None):
        # 127.0.0.1 3306 root 123456 information_schema
        self.host = host
        self.port = port
        self.user = user
        self.password = password
        self.db = db
        self.loop = loop or asyncio.get_event_loop()

    async def connect_pool(self):
        if self.pool:
            return self.pool
        self.pool = await aiomysql.create_pool(
            host=self.host or os.getenv("database_host"),
            port=self.port or eval(os.getenv("database_port")),
            user=self.user or os.getenv("database_user"),
            password=self.password or os.getenv("database_password"),
            db=self.db or os.getenv("database_db"),
            loop=self.loop
        )
        return self.pool

    async def close(self):
        """关闭数据库连接池"""
        if self.pool:
            self.pool.close()
            await self.pool.wait_closed()

    async def execute(self, sql, *args) -> tuple:
        pool = await self.connect_pool()
        async with pool.acquire() as conn:
            conn: aiomysql.Connection
            # 异步的上下文管理 游标对象
            async with conn.cursor(aiomysql.DictCursor) as cursor:
                cursor: aiomysql.Cursor
                await self.show_sql_log(sql, *args)
                await cursor.execute(sql, args)
                result: tuple = await cursor.fetchall()
                return result

    async def show_sql_log(self, sql, *args):
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
        logging.debug(f"【SQL】: {formatted_sql}")

    async def select(self, table, columns='*', where=None, order_by=None, limit=None):
        """输入表名进行查询"""
        query = f"SELECT {columns} FROM {table}"
        if where:
            query += f" WHERE {where}"
        if order_by:
            query += f" ORDER BY {order_by}"
        if limit:
            query += f" LIMIT {limit}"
        return await self.execute(query)

    async def insert(self, table, data):
        placeholders = ', '.join(['%s'] * len(data))
        columns = ', '.join(data.keys())
        values = tuple(data.values())
        query = f"INSERT INTO {table} ({columns}) VALUES ({placeholders})"
        return await self.execute(query, values)

    async def update(self, table, data, where):
        updates = ', '.join([f"{key} = %s" for key in data.keys()])
        values = tuple(data.values())
        query = f"UPDATE {table} SET {updates} WHERE {where}"
        return await self.execute(query, values)

    async def delete(self, table, where):
        query = f"DELETE FROM {table} WHERE {where}"
        return await self.execute(query)

    async def async_for_cursor(self, sql):
        """游标迭代，拉取一小部分数据（通常是内部缓冲区大小的数据），逐行返回"""
        pool = await self.connect_pool()
        async with pool.acquire() as conn:
            conn: aiomysql.Connection
            async with conn.cursor(aiomysql.DictCursor) as cursor:
                cursor: aiomysql.cursors.Cursor
                await cursor.execute(sql)
                # results = await cursor.fetchall()
                async for row in cursor:
                    yield row

    async def fetchmany_until_over(self, sql, *args, size=100):
        """分批次获取结果，一次获取100条记录直到为空"""
        pool = await self.connect_pool()
        async with pool.acquire() as conn:
            # 游标结果返回字典格式
            async with conn.cursor(aiomysql.DictCursor) as cur:
                cur: aiomysql.cursors.Cursor
                await cur.execute(sql, args)
                while True:
                    results = await cur.fetchmany(size=size)
                    if not results:
                        break
                    yield results


def main():
    async def asy_query():
        rows = []
        async for row in AioMySQLClient().async_for_cursor(sql="select * from qiye_declareable_project limit 2"):
            print(row)
            rows.append(row)
        return rows
    return asyncio.run(asy_query())


if __name__ == '__main__':
    print(main())
