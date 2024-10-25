# encoding:utf-8
import logging

import requests
import base64

from aip import AipOcr


# https://ai.baidu.com/ai-doc/OCR/Ck3h7y2ia
def get_access_token(client_id, client_secret):
    # client_id 为官网获取的AK， client_secret 为官网获取的SK
    host = f'https://aip.baidubce.com/oauth/2.0/token?grant_type=client_credentials&client_id={client_id}&client_secret={client_secret}'
    response = requests.get(host)
    access_token = response.json()['access_token']
    return access_token


# https://ai.baidu.com/ai-doc/OCR/zk3h7xz52
def baidu_orc_general_basic2(filename, access_token):
    """
    通用文字识别
    filename: 本地文件
    access_token: [调用鉴权接口获取的token]
    """
    request_url = "https://aip.baidubce.com/rest/2.0/ocr/v1/general_basic"
    # 二进制方式打开图片文件
    f = open(filename, 'rb')
    img = base64.b64encode(f.read())

    params = {"image": img}
    request_url = request_url + "?access_token=" + access_token
    headers = {'content-type': 'application/x-www-form-urlencoded'}
    response = requests.post(request_url, data=params, headers=headers)
    result = response.json()
    if result.get('words_result') is None:
        logging.error(result)
        return None
    text = ""
    for i in result.get('words_result'):
        if i == 0:
            text = i.get('words')
        else:
            text += "\n" + i.get('words')
    return text


def baidu_orc_general_basic(img_name):
    """
    通用文字识别
    img_name: 本地图片
    return: 识别结果
    """
    text = ""
    APP_ID = '115896386'
    API_KEY = 'BjvIG8O9uXLOXWGcpBB3CTZ6'
    SECRET_KEY = 'q7NLp5cZ4DzHGt057Sc3gUJ8ClKZ5snK'

    client = AipOcr(APP_ID, API_KEY, SECRET_KEY)
    img = open(f'{img_name}', 'rb').read()
    # 标准版
    result = client.basicGeneral(img)
    if result.get('words_result') is None:
        logging.error(result)
        return ""
    for i in result.get('words_result'):
        if text == "":
            text += (i.get('words'))
        else:
            text += "\n" + i.get('words')
    return text
