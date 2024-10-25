import requests


def translate(q='hello world'):
    res = requests.get('http://142.250.0.161/translate_a/single?client=at&sl=en&tl=zh-CN&dt=t&q=%s' % q,
                       headers={'Host': 'translate.googleapis.com'})
    # res = requests.get('https://142.250.0.161/translate_a/single?client=at&sl=en&tl=zh-CN&dt=t&q=%s' % q,
    #                    headers={'Host': 'translate.googleapis.com'}, verify=False)
    return res.text


if __name__ == '__main__':
    print(translate())
