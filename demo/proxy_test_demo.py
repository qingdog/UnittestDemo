import logging
import time

import requests
from bs4 import BeautifulSoup
from requests.exceptions import ReadTimeout, ConnectionError

import utils.multiprocess_util
from utils import color_format_logging

color_format_logging.main()
logger = logging.getLogger()


def test_proxy(ip_port: str, username=None, password=None, url='https://fanyi.baidu.com/', timeout=3):
    """测试单个代理
    :param ip_port: 127.0.0.1:80
    :return: 请求响应耗时
    """
    username_password = ""
    if username and password: username_password = f"{username}:{password}@"
    proxies = {'http': f'http://{username_password}{ip_port}', 'https': f'http://{username_password}{ip_port}'}

    # 发送请求，设置5秒超时
    start_time = time.time()
    response_time = None
    try:
        response = requests.get(url, proxies=proxies, timeout=(timeout, timeout * 2))
        response_time = time.time() - start_time

        response.encoding = response.apparent_encoding  # 解决乱码问题
        if response.status_code == 200:
            logger.debug(response.text)  # 打印响应内容

            page = response.text
            soup = BeautifulSoup(page, 'lxml')
            logger.info(f"代理：{ip_port} 耗时：{response_time}{soup.find('title')}")
    except ReadTimeout as e:
        logger.warning(f"{ip_port} {e}")
    except ConnectionError as e:
        logger.warning(f"{time.time() - start_time}s {ip_port} {e}", exc_info=False)
    except Exception as e:
        raise e
    # 异常则返回 超时时间+1s
    return response_time if response_time else timeout + 1


def multi_test_proxy(ip: str, timeout_avg=3):
    """
    多次测试代理取平均值比较是否超过平均值，超过了平均值则返回None
    """
    logger.debug(f"{ip} ...")
    consumes = []
    for i in range(3):  # 循环三次
        consume = test_proxy(ip, timeout=timeout_avg)
        consumes.append(consume)
    avg = sum(consumes) / len(consumes)
    if avg < timeout_avg:
        logger.critical(f"{ip} 平均耗时：{avg}")
        return ip
    return None


if __name__ == '__main__':
    """
快代理：https://www.kuaidaili.com/free/#（已使用动态加载安全保护，爬不了（能力不足），弃）（其中的优质私密代理还是挺好的）
proxy-list.download：https://www.proxy-list.download/#（直接调api接口，可爬）选择了https/SSL每天更新一次
开心代理：http://www.kxdaili.com/dailiip.html#（可爬）选择了高匿+https大概是每60min更新一次
小幻代理：https://ip.ihuan.me/#（可爬，网站要求控制速度）选择了高匿+https+post每天更新一次
云代理：http://www.ip3366.net/#（可爬（没试过），看起来https的较少以及不能翻页的爬虫警告，弃）
89代理：https://www.89ip.cn/#（可爬（没试过），但无高匿筛选，弃）
国外free-proxy-list：https://free-proxy-list.net/#（无反爬机制）选择了elite+https每10min更新一次
    """
    # logger.remove()
    # handler_id = logger.add(sys.stderr, level="INFO")

    with open("proxy_test.txt", 'r') as file:
        all_proxy_list = [line.strip() for line in file]
    logger.info(f"check_proxy: {all_proxy_list}")
    ips = []

    '''stime = time.time()
    for i in all_proxy_list:
        check_ip = multi_test_proxy(i)
        if check_ip: ips.append(check_ip)
    logger.info(time.time() - stime)'''

    # 使用多进程来执行测试
    for check_ip in utils.multiprocess_util.submit_to_multiprocess(multi_test_proxy, all_proxy_list):
        if check_ip: ips.append(check_ip)
        logger.critical(check_ip, exc_info=False)

    logger.critical(ips, exc_info=False)
