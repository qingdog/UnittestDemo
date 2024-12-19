import asyncio
import aiomysql


class MySQLPool:
    def __init__(self, host, port, user, password, db, loop=None, autocommit=False, minsize=1, maxsize=10):
        self.host = host
        self.port = port
        self.user = user
        self.password = password
        self.db = db
        self.loop = loop or asyncio.get_event_loop()
        self.autocommit = autocommit
        self.minsize = minsize
        self.maxsize = maxsize
        self.pool = None

    async def init_pool(self):
        self.pool = await aiomysql.create_pool(
            host=self.host,
            port=self.port,
            user=self.user,
            password=self.password,
            db=self.db,
            loop=self.loop,
            autocommit=self.autocommit,
            minsize=self.minsize,
            maxsize=self.maxsize
        )

    async def execute(self, query, *args):
        if not self.pool:
            raise Exception("MySQL pool is not initialized. Call init_pool() first.")
        async with self.pool.acquire() as conn:
            async with conn.cursor() as cur:
                await cur.execute(query, args)
                return await cur.fetchall()

    async def close(self):
        if self.pool:
            self.pool.close()
            await self.pool.wait_closed()


# 使用示例
if __name__ == '__main__':
    async def main():
        mysql_pool = MySQLPool(host='192.168.50.205', port=3306, user='liqi_qiye_test', password='cABbY6rmS2LDtKPN',
                               db='liqi_qiye_test')
        await mysql_pool.init_pool()

        # 执行查询
        result = await mysql_pool.execute("SELECT 10")
        print(result)

        # 关闭连接池
        await mysql_pool.close()


    loop = asyncio.get_event_loop()
    loop.run_until_complete(main())
