import asyncio
import logging
import math
import time

from databases.aiomysql_client import AioMySQLClient


async def fetch_data(client, start, end):
    # 修改为异步查询数据的代码
    table_name = 'qiye_base_business'
    query = f"SELECT * FROM {table_name} LIMIT {start}, {end - start}"
    return await client.execute(query)


async def fetch_data_count():
    total_rows = 0
    async for row in AioMySQLClient().async_for_cursor(sql="select count(*) from qiye_base_business"):
        row: dict
        total_rows = row.get("count(*)")
    return total_rows


async def main():
    """一次查询1w条数据，20次查询作为一批给协程执行。直到查询完所有数据"""
    client = AioMySQLClient()
    total_rows = await fetch_data_count()
    print(total_rows)

    batch_size = 10000  # 查询的表和每批次的大小
    times = 20
    num_batches: int = math.ceil(total_rows / batch_size / times)  # 计算需要多少批次

    s = time.time()
    # 异步处理每个批次
    for i in range(num_batches):
        tasks = []
        for j in range(times):
            start = batch_size * (j + i * times)
            end = (j + 1 + i * times) * batch_size
            if end > total_rows:
                end = total_rows
                tasks.append(fetch_data(client, start, end))
                break
            tasks.append(fetch_data(client, start, end))

        # 执行所有任务
        start_time = time.time()
        try:
            results = await asyncio.gather(*tasks)
            # 处理结果
            length = 0
            for data in results:
                length = len(data)
            print(f"Fetched {len(results) * length} records")
        except Exception as e:
            raise e
        finally:
            logging.info(time.time() - start_time)
    logging.warning(f"{time.time() - s} done.")


def cpu_task():
    for _ in range(1000000000): pass


if __name__ == '__main__':
    import utils.color_format_logging

    utils.color_format_logging.main()
    import sysconfig

    print("Py_GIL_DISABLED", sysconfig.get_config_vars().get("Py_GIL_DISABLED"))
    # asyncio.run(main())

    import multiprocessing

    # for i in range(12): multiprocessing.Process(target=cpu_task).start()
