import logging
import threading
import time

import requests
from bs4 import BeautifulSoup
from fake_useragent import UserAgent


def test_proxy(ip, proxy_response_times, lock, max_times, timeout=5):
    """
    Function to test a single proxy
    :param ip:
    :param proxy_response_times:
    :param lock:
    :param max_times:
    :param timeout:
    :return:
    """
    error_code_times = 0
    start_time = time.time()
    for i in range(max_times):
        res = None
        try:
            res = requests.get('https://fanyi.baidu.com/', proxies={"https": f"http://{ip}"},
                               headers={'User-Agent': UserAgent().random, }, timeout=timeout)
        except Exception as e:
            logging.error(e)
        if res.status_code == 200 and res is not None:
            res.encoding = res.apparent_encoding
            page = res.text
            soup = BeautifulSoup(page, 'lxml')
            title = soup.find('h1').text
            # if title == 'Example Domain':
            #     if (i + 1) % 10 == 0:
            #         print("success", i + 1, ip)
        else:
            error_code_times += 1
            if error_code_times == 3:
                start_time -= timeout
                break
    # Calculate the response time
    response_time = (time.time() - start_time) / max_times
    # 小于2s将代理及其响应时间存储在字典中
    if response_time < 2:
        with lock:  # 使用锁
            proxy_response_times[ip] = response_time


# Main function to test a list of proxies
def test_pressure(ip_list, thread_number=8, max_times=40):
    """
    压力测试 启用线程测试多个
    :param ip_list: 代理ip
    :param max_times: 最大压的次数
    :return:
    """
    length = len(ip_list)
    print(length)
    proxy_response_times = {}
    threads = []
    lock = threading.Lock()  # 创建锁

    # 每16个线程一次
    for i in range(0, length, thread_number):  # 每次处理16个IP
        # 创建并启动每个代理的线程
        for j in range(i, min(i + thread_number, length)):  # 确保不会超出IP列表的范围
            t = threading.Thread(target=test_proxy, args=(ip_list[j], proxy_response_times, lock, max_times))
            threads.append(t)
            t.start()

        # 等待当前批次的16个线程完成
        for t in threads[i:i + thread_number]:  # 只等待当前批次的线程
            t.join()  # 等待所有线程结束
        print(f"第{i // thread_number + 1}批次线程已完成")

    # Sort the proxies by response time, from fastest to slowest
    sorted_proxies = sorted(proxy_response_times.items(), key=lambda item: item[1])
    s_proxies = []
    # Print the sorted list of proxies
    for proxy, t in sorted_proxies:
        print(f"{proxy}: {t:.3f}秒")
        s_proxies.append(proxy)
    return s_proxies
