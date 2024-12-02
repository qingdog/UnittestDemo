import json
import logging
import re

import requests
from requests import Response

from utils.myutil import get_latest_file_path


class HarRequestTool:
    def __init__(self, har_file_path):
        """
        初始化工具类，读取并解析HAR文件。
        :param har_file_path: HAR文件路径
        """
        self.har_file_path = har_file_path
        self.har_data = self._load_har_file()
        self.entries_len = len(self.har_data['log']['entries'])
        self.session = requests.session()

    def _load_har_file(self):
        """
        读取并解析HAR文件。
        :return: HAR文件内容（字典）
        """
        with open(self.har_file_path, 'r', encoding='utf-8') as f:
            return json.load(f)

    def get_request_details(self, entry_index: int):
        """
        获取指定索引位置的请求详情。
        :param entry_index: 请求条目的索引
        :return: 请求方法、URL、请求头、请求体、索引
        """
        entry = self.har_data['log']['entries'][entry_index]
        request_data = entry['request']

        method: str = request_data['method']
        url: str = request_data['url']
        # request 过滤掉不支持的HTTP/2中带有冒号的字段（如：':authority'）
        headers = {
            header['name']: header['value']
            for header in request_data.get('headers', [])
            if not header['name'].startswith(':')
        }

        body: str = request_data.get('postData', {}).get('text', '')  # 获取请求体（如果存在）
        return method, url, headers, body, entry_index

    def send_requests(self, entries_index: int = None, ) -> list[Response]:
        """
        循环执行所有请求（遍历HAR文件中的所有条目），发送所有请求。
        :entries_index: 指定单个请求
        :return: 每个请求的响应列表
        """
        response_result = []
        if entries_index:
            return [self.send(*self.get_request_details(entries_index))]
        for index in range(self.entries_len):
            response = self.send(*self.get_request_details(index))
            response_result.append(response)
        return response_result

    def send(self, method, url, headers, body, index=0):
        response: Response = self.session.request(method=method, url=url, headers=headers, data=body, timeout=10)
        return response


def main(re_pattern):
    session = requests.session()
    import utils.color_format_logging
    logging.getLogger().setLevel(logging.INFO)
    har_tool = HarRequestTool(get_latest_file_path("..", ".har"))
    for index in range(har_tool.entries_len):
        method, url, headers, body, index = har_tool.get_request_details(index)
        if re.search(re_pattern, url):
            # logging.debug(f"登录码{index}: {headers.get("Authorization")}")
            logging.info(f"请求{index}: {url}")
            res = session.request(method=method, url=url, headers=headers, data=body)
            logging.info(f"结果{index}: {res.text}")


if __name__ == "__main__":
    main(r"test-api")
    # responses = HarRequestTool("cloud.har").send_requests()  # 输出每个请求的响应信息
    # for res in responses:
    #     print(res.text)
