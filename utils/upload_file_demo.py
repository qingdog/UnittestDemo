import requests


def upload(file_path):
    # 设置上传的目标URL
    upload_url = 'https://test-lqc-api.liqicloud.com/app/applet/action/feedback/upload'

    # 省略 Content-Type 头，让request自动处理上传文件的边界 'Content-Type': 'multipart/form-data; boundary=1729157996591,'
    headers = {
        'Authorization': 'eyJhbGciOiJIUzUxMiJ9.eyJ1c2VyX2lkIjoxODQwNjc4OTQ0MzQwMzgxNjk3fQ.aeyslq073lFygeQBHqUjm4IiIhPahN6vk8N0kgtsncJpuAj0HsoatuefzsvGSIyxvp4bwpv74IsCgr42-hT_KA',
        # 'User-Agent': 'Mozilla/5.0 (Linux; Android 11; M2006J10C Build/RP1A.200720.011; wv) AppleWebKit/537.36 (KHTML, like Gecko) Version/4.0 Chrome/116.0.0.0 Mobile Safari/537.36 XWEB/1160117 MMWEBSDK/20240104 MMWEBID/4488 MicroMessenger/8.0.48.2590(0x28003045) WeChat/arm64 Weixin GPVersion/1 NetType/WIFI Language/zh_CN ABI/arm64 MiniProgramEnv/android',
        # 'Accept-Encoding': 'gzip,compress,br,deflate',
        # 'Platform': 'mp-weixin',
        # 'Referer': 'https://servicewechat.com/wxd0b9721dae1a4f10/0/page-frame.html'
    }

    # 要上传的文件路径
    # file_path = 'path/to/your/tmp_509af695912297f3f8b6a66ab5e7bb6349caa351375e58da.jpg'  # 替换为实际的文件路径
    # file_path = "D:/Downloads/python-3.8.8-amd64.exe"

    # 准备文件
    with open(file_path, 'rb') as f:
        #        'file' 是字段的名称
        files = {'file': f}
        # files = {'file': (f.name, f, 'image/jpeg')}

        # 发送POST请求
        response = session.request(method='POST', url=upload_url, headers=headers, files=files)

    # 输出响应状态码和响应内容
    print(response.status_code)
    print(response.text)


if __name__ == '__main__':
    # 创建一个会话对象
    session = requests.Session()
    upload('D:/mytest/UnittestDemo/utils/2.png')
    # 关闭会话
    session.close()
