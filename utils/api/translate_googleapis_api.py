import socket

import requests


def translate(q='hello world'):
    headers = {'Host': 'translate.googleapis.com'}
    res = requests.get(f'http://142.250.0.161/translate_a/single?client=at&sl=en&tl=zh-CN&dt=t&q={q}', headers=headers, verify=False, timeout=5)
    # res = requests.get('https://142.250.0.161/translate_a/single?client=at&sl=en&tl=zh-CN&dt=t&q=%s' % q,
    # headers={'Host': 'translate.googleapis.com'}, verify=False)
    return res.text


def translate_html():
    print(socket.gethostbyname_ex("translate-pa.googleapis.com"))  # 142.250.0.161
    html = [[["nacos", "HOME", "DOCS", "BLOG", "COMMUNITY"], "en", "zh-CN"], "te_lib"]
    headers = {'Host': 'translate-pa.googleapis.com', 'X-goog-api-key': 'AIzaSyATBXajvzQLTDHEQbcpq0Ihe0vWDHmO520', 'Content-Type': 'application/json+protobuf'}
    # headers["X-Client-Data"] = "CI22yQEIprbJAQipncoBCK+NywEIkqHLAQiBo8sBCIWgzQEI9c/OARjBy8wB"
    res = requests.post(url="https://translate-pa.googleapis.com/v1/translateHtml", json=html, headers=headers)
    return res.text


if __name__ == '__main__':
    print(translate())
    # print(translate_html())
