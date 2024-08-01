import sys
import time

import requests
from bs4 import BeautifulSoup
from requests.exceptions import Timeout
from loguru import logger

import youdao_translate


# 设置代理服务器地址和端口
# proxies = {
#     'http': 'http://120.25.1.15:7890',
#     'https': 'http://120.25.1.15:7890',
# }


def open_proxy(txt):
    """依次读取下一行放入列表中"""
    with open(txt, 'r') as file:
        ip_list = [line.strip() for line in file]
        logger.info(f"{txt} {ip_list}")
    return ip_list


def test_proxy(ip_port,username=None,password=None, timeout=5):
    # 要请求的URL
    url = 'https://fanyi.baidu.com/'

    login = ""
    if username and password:
        login = f"{username}:{password}@"
    proxies = {
        'http': f'http://{login}{ip_port}',
        'https': f'http://{login}{ip_port}'
    }

    # 发送请求，设置5秒超时
    start_time = time.time()
    try:
        response = requests.get(url, proxies=proxies, timeout=timeout)
        response.encoding = response.apparent_encoding  # 解决乱码问题
        # 打印响应内容
        logger.debug(response.text)
        # 计算响应时间
        response_time = time.time() - start_time
        title = None
        if response.status_code == 200:
            page = response.text
            soup = BeautifulSoup(page, 'lxml')
            # if (soup.find('h1'))
            title = " 标题：" + soup.find('h1').text if soup.find('h1') else ""

        logger.info(f"代理：{ip_port} 耗时：{response_time}{title}")
        return response_time
    except Timeout as t:
        # 捕获超时异常
        logger.warning(f"{ip_port} {t}")
        logger.debug(f"代理访问接口耗时：{time.time() - start_time}")
    except requests.exceptions.RequestException as e:
        # 打印其他请求异常信息
        logger.error(f"{ip_port} {e}")
        logger.debug(f"代理访问接口耗时：{time.time() - start_time}")
    return 0


def write_proxy(proxy):
    with open('./proxies.txt', 'a') as f:  # 存储在本地的proxies.txt文件中，注意路径问题
        f.write(f"{proxy}\n")  # 每行写入一个代理IP


def check_proxy(ip_list):
    """
    检查代理ip是否有效
    """
    if not ip_list:
        return

    for ip in ip_list:
        consumes = []
        for i in range(3):
            consume = test_proxy(ip)
            consumes.append(consume)
            if consume < 1:
                break
        if consumes[0] == 0:
            continue
        avg = sum(consumes) / len(consumes)
        if avg > 5:
            break
        logger.warning(f"{ip} 平均耗时：{avg}")
        write_proxy(ip)

    ip_list = open_proxy("./proxies.txt")
    for ip in ip_list:
        consumes = []
        for i in range(3):
            consume = test_proxy(ip)
            consumes.append(consume)
            if consume < 1:
                if consume == 0:
                    consumes.clear()
                break
        if not consumes:
            continue
        avg = sum(consumes) / len(consumes)
        if avg > 5:
            break
        logger.warning(f"{ip} 平均耗时：{avg}")
        write_proxy(ip)


if __name__ == '__main__':
    logger.remove()
    handler_id = logger.add(sys.stderr, level="INFO")

    logger.info(youdao_translate.YoudaoTranslate2024().translate("i have to go"))

    check_proxy(open_proxy('./proxies_test.txt'))
