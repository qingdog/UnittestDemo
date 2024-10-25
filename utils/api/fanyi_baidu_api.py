import hashlib
import json
import random

import requests


def generate_random_number():
    return random.randint(1000, 10000)


def calculate_md5(input_str):
    # 创建md5对象
    md5_hash = hashlib.md5()
    # 需要确保输入的字符串是字节串
    md5_hash.update(input_str.encode('utf-8'))
    # 返回16进制格式的MD5哈希值
    return md5_hash.hexdigest()


def fanyi_api_baidu(q="hello", from_lang="en", to="zh", appid="20201126000626290", secret_key="qTdrCuOJXbbKjcgD8dZN"):
    headers = {
        "Content-Type": "application/x-www-form-urlencoded"
    }
    salt = generate_random_number()
    sign = calculate_md5(f"{appid}{q}{salt}{secret_key}")
    url = f"https://fanyi-api.baidu.com/api/trans/vip/translate?q={q}&from={from_lang}&to={to}&appid={appid}&salt={salt}&sign={sign}"
    res = requests.get(url, headers=headers)
    return decode_unicode(res.text)


def decode_unicode(text):
    return text.encode('utf-8').decode('unicode_escape')


def get_translate_result(json_text):
    # 将JSON字符串解析为Python字典
    translate_result = json.loads(json_text)
    return translate_result["trans_result"][0]["dst"]


if __name__ == '__main__':
    print(get_translate_result(fanyi_api_baidu()))
