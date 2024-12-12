import json
import logging
import os
import re

import requests
from requests import Response

from utils.login_ruoyi_verification_code import login_verification_code
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

    def _read_body_from_file(self, file_name):
        """
        从文件中读取请求体内容。
        :param file_name: 文件名
        :return: 文件内容
        """
        # 获取 self.har_file_path 所在的目录
        har_file_dir = os.path.dirname(self.har_file_path)
        file_path = os.path.join(har_file_dir, file_name)
        if not os.path.exists(file_path):
            raise FileNotFoundError(f"Body file '{file_path}' not found.")
        with open(file_path, 'r', encoding='utf-8') as f:
            return f.read()

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

        # 获取请求体
        dict_data = {}
        post_data = request_data.get('postData', {})
        body = post_data.get('text', '').strip()

        # 如果 body 为空，则尝试从 _file 中读取
        if not body and "_file" in post_data:
            body = self._read_body_from_file(post_data["_file"])
        if body:
            try:
                dict_data = json.loads(body)  # 转换为字典
            except json.JSONDecodeError as e:
                print(f"解析错误: {e}")

        return method, url, headers, dict_data, entry_index

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
        response: Response = self.session.request(method=method, url=url, headers=headers, json=body, timeout=10)
        return response


def main(url_re_pattern):
    session = requests.session()
    from utils import color_format_logging
    color_format_logging.main()
    logging.getLogger().setLevel(logging.DEBUG)
    har_tool = HarRequestTool(get_latest_file_path("", ".har"))
    for index in range(har_tool.entries_len):
        method, url, headers, body, index = har_tool.get_request_details(index)
        if re.search(url_re_pattern, url):
            headers["Authorization"] = login_verification_code()
            body = {"pageSize":10,"pageNo":1,"name":"青岛市就业创业政策清单（家庭服务业商业综合保险补贴）"}
            logging.debug(f"请求{index}: {url} {body}")
            res = session.request(method=method, url=url, headers=headers, json=body)
            logging.info(f"结果{index}: {res.text}")
            break


if __name__ == "__main__":
    main(url_re_pattern=r"project.select")
    # responses = HarRequestTool("cloud.har").send_requests()  # 输出每个请求的响应信息
    # for res in responses:
    #     print(res.text)
