from multiprocessing import Pool
import time
import logging
from typing import Callable, List


def sleep_2_seconds(p=1):
    time.sleep(2)
    return p * 2


def chunked(iterable, size):
    """将 iterable 分割成大小为 size 的块"""
    for i in range(0, len(iterable), size):
        yield iterable[i:i + size]


def submit_to_multiprocess(task: Callable, tasks_args: list, batch_size=10) -> List:
    """使用进程池来执行，默认10个进程执行完返回一批数据"""
    start_time = time.time()
    with Pool() as pool:
        # 调用 chunked 函数将 tasks_args 列表分割为多批次
        for task_chunk in chunked(tasks_args, batch_size):
            # 使用 pool.map 或 pool.starmap 来批量处理任务
            results = pool.map(task, task_chunk)  # 等待所有任务完成并获取结果
            yield results
            '''results = []
            # 异步执行任务
            for task_arg in task_chunk:
                # 通过回调函数将返回值入队
                pool.apply_async(task, args=(task_arg,), callback=lambda result: result_queue.put(result))

            # 等待所有结果并获取
            while len(results) < len(task_chunk):
                results.append(result_queue.get())  # 获取结果'''

    logging.info(f"执行总耗时：{time.time() - start_time}s")


if __name__ == '__main__':
    logging.basicConfig(level=logging.INFO)

    for chunk in submit_to_multiprocess(sleep_2_seconds, [1, 2, 3, 4, 5], batch_size=4):
        print(chunk)
