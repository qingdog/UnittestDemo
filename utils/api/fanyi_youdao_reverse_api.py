import base64
import hashlib
import json
import time

import requests
from Crypto.Cipher import AES  # pip install pycryptodome
from Crypto.Util.Padding import unpad
from fake_useragent import UserAgent


class YoudaoTranslate2024(object):
    # 初始化参数
    def __init__(self):
        # 请求的url
        self.url = "https://dict.youdao.com/webtranslate"
        # 封装请求头，要求和网易请求一致
        self.headers = {
            "Cookie": 'OUTFOX_SEARCH_USER_ID_NCOO=1948382659.381789; OUTFOX_SEARCH_USER_ID=1775497575@183.219.26.105; __yadk_uid=5QwMgTGcByPM5Fdhip58d5m1lBPBpGCW; rollNum=true; ___rl__test__cookies=1708157820132',
            "Referer": "https://fanyi.youdao.com/",
            "User-Agent": UserAgent().random
            # "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/123.0.0.0 Safari/537.36"
        }

    # 该函数用于封装data
    def get_mysticTime_sign(self):
        mysticTime = str(int(time.time() * 1000))
        secretKey = 'fsdsogkndfokasodnaso'
        client = "fanyideskweb"
        product = "webfanyi"
        # string = 'client={u}&mysticTime={e}&product={d}&key={t}'.format(u=u, e=e, d=d, t=t)
        string = f'client={client}&mysticTime={mysticTime}&product={product}&key={secretKey}'
        sign = hashlib.md5(string.encode()).hexdigest()
        return mysticTime, sign

    def md5_digest(self, e):
        return hashlib.md5(e.encode()).digest()  # .digest()返回二进制的值

    def encrypt_data(self, t):
        """解码翻译后文本
           https://dict.youdao.com/webtranslate/key?keyid=webfanyi-key-getter&sign=34766a2ab8e0da97617743bf24355370&client=fanyideskweb&
           product=webfanyi&appVersion=1.0.0&vendor=web&pointParam=client,mysticTime,product&mysticTime=1722910162533&keyfrom=fanyi.web&
           mid=1&screen=1&model=1&network=wifi&abtest=0&yduuid=abcdefg
        """
        aesKey = 'ydsecret://query/key/B*RGygVywfNBwpmBaZg*WT7SIOUP2T0C9WHMZN39j^DAdaZhAnxvGcCY6VYFwnHl'
        aesIv = 'ydsecret://query/iv/C@lZe2YzHtZ2CYgaXKSVfsb7Y4QWHjITPPZ0nQp87fBeJ!Iv6v^6fvi2WN@bYpJ4'
        a = self.md5_digest(aesKey)[:16]  # 取前16位
        i = self.md5_digest(aesIv)[:16]  # 取前16位
        r = AES.new(a, AES.MODE_CBC, i)  # 创建一个AES对象（密钥，模式，偏移量）aes.MODE_CBC是加密模式,a表示密钥，i表示偏移量
        s = r.decrypt(base64.urlsafe_b64decode(t))  # 解码为原始的字节串
        return unpad(s, AES.block_size).decode('utf-8')  # AES.block_size = 16 ,解密后去掉填充的字符 返回解密后的字符串

    def translate(self, input_text="hello", proxies=None):
        """
        有道翻译逆向
        https://blog.csdn.net/qq_44990881/article/details/136142933
        :param input_text: 请输入待翻译文本
        :param proxies: proxies={"https": f"http://127.0.0.1:80"}
        :return: 翻译的结果
        """
        if proxies is str:
            proxies = {"https": f"http://{proxies}"}
        mysticTime, sign = self.get_mysticTime_sign()
        # 定义data
        data = {
            'i': input_text,
            'from': 'auto',
            'to': '',
            'dictResult': 'true',
            'keyid': 'webfanyi',
            'sign': sign,
            'client': 'fanyideskweb',
            'product': 'webfanyi',
            'appVersion': '1.0.0',
            'vendor': 'web',
            'pointParam': 'client,mysticTime,product',
            'mysticTime': mysticTime,
            'keyfrom': 'fanyi.web',
            'mid': '1',
            'screen': '1',
            'model': '1',
            'netword': 'wifi',
            'abtest': '0',
            'yduuid': 'abcdefg',
        }
        # 用post做请求,获得json输出，便于我们提取数据 请求结果格式为：{"code":0,"dictResult":{"ec":{"exam_type":["初中","高中","CET4","CET6",
        # "考研"],"word":{"usphone":"ˈæp(ə)l","ukphone":"ˈæp(ə)l","ukspeech":"apple&type=1","trs":[{"pos":"n.",
        # "tran":"苹果"}],"wfs":[{"wf":{"name":"复数","value":"apples"}}],"return-phrase":"apple",
        # "usspeech":"apple&type=2"}}},"translateResult":[[{"tgt":"苹果","src":"apple","tgtPronounce":"pín guŏ"}]],
        # "type":"en2zh-CHS"}
        response_text = requests.post(url=self.url, data=data, headers=self.headers, proxies=proxies).text

        result = self.encrypt_data(response_text)
        result = json.loads(result)['translateResult'][0][0]['tgt']
        return result


if __name__ == '__main__':
    print(YoudaoTranslate2024().translate("i have to go"))
