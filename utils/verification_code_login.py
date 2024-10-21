# 方法一  直接在读取图片的时候灰度化
import base64
import json
import logging
import re

import cv2
import numpy as np
import requests
from aip import AipOcr

# import muggle_ocr


# pip install opencv-python numpy muggle_ocr

# https://fuping.site/2022/01/19/Calculate-Captcha-Recognition/
# https://zhuanlan.zhihu.com/p/392269519
def image_grayscale(filename, fun=3):
    """灰度化"""
    if fun == 1:
        # 方法一  直接在读取图片的时候灰度化
        verification_code = cv2.imread(filename, cv2.IMREAD_GRAYSCALE)
    elif fun == 2:
        # 方法二 在读入图片后再进行灰度化
        verification_code = cv2.imread(filename)
        # verification_code = cv2.cvtColor(verification_code, cv2.COLOR_BGR2GRAY)
    else:
        # 方法三  使用numpy取值进行灰度化
        # max:取最大值 较亮      min：取最小值  较黑      mean：取平均值
        verification_code = cv2.imread(filename)
        verification_code = np.min(verification_code, axis=2).astype(np.uint8)
    return verification_code


def show_img(verification_code):
    """windows显示图片"""
    # 显示灰度化的图片  windows1是窗口名称
    cv2.imshow('windows1', verification_code)
    # waitKey()–是在一个给定的时间内(单位ms)等待用户按键触发，0表示任意按键
    cv2.waitKey(0)
    # 销毁特定的窗口
    cv2.destroyWindow('windows1')


def image_binary(verification_code, thresh=160):
    """将图片变成黑白（0和255）进行二值化处理"""
    # 像素值大于等于 160 阈值（表示图像中像素强度的分界线），设置成 255 白色
    thresh, yzm = cv2.threshold(verification_code, thresh=thresh, maxval=255, type=cv2.THRESH_BINARY)
    # 自适应阈值二值化处理
    # yzm = cv2.adaptiveThreshold(yzm, 255, cv2.ADAPTIVE_THRESH_GAUSSIAN_C, cv2.THRESH_BINARY, 11, 2)
    return yzm


def image_noise_reduction(verification_code, fun=1):
    """图片降噪"""
    if fun == 1:
        # 方法一 cv2中的morphologyEx方法
        # 1.开运算（Opening）：
        # 去噪：它是先进行侵蚀，再进行膨胀，常用于去除小的噪点，适合去除白色噪声。cv2.MORPH_OPEN
        # 2.闭运算（Closing）：
        # 修复小孔：它是先进行膨胀，再进行侵蚀，常用于填补黑色区域的细小孔洞，适合去除黑色噪声。cv2.MORPH_CLOSE
        # 3.形态学梯度（Morphological Gradient）：
        # 轮廓增强：膨胀结果与侵蚀结果的差值，常用于提取物体边缘。cv2.MORPH_GRADIENT
        # 4.顶帽运算（Top Hat）：
        # 突出亮区域：图像与其开运算结果的差值，常用于提取比其周围区域更亮的小区域。 cv2.MORPH_TOPHAT
        # 5.黑帽运算（Black Hat）：
        # 突出暗区域：闭运算结果与图像的差值，常用于提取比其周围区域更暗的小区域。 cv2.MORPH_BLACKHAT
        verification_code = cv2.morphologyEx(verification_code, cv2.MORPH_CLOSE, np.ones(shape=(6, 6)))
    elif fun == 2:
        # 方法二 使用侵蚀与膨胀形态学去噪
        # 先膨胀 让黑色噪点消失，再侵蚀让黑色加粗
        dilate = cv2.dilate(verification_code, np.ones(shape=(6, 6)))
        verification_code = cv2.erode(dilate, np.ones(shape=(5, 5)))
    # 使用侵蚀与膨胀形态学去噪
    elif fun == 3:
        # 八邻域降噪
        pass
    else:
        # 逐渐增大核的尺寸，观察字符完整性
        # 创建一个 3x3 的矩形核
        kernel = cv2.getStructuringElement(cv2.MORPH_RECT, (3, 3))
        # 应用开运算去噪
        verification_code = cv2.morphologyEx(verification_code, cv2.MORPH_OPEN, kernel)
        show_img(verification_code)
        # 或者创建一个 5x5 的椭圆形核
        kernel = cv2.getStructuringElement(cv2.MORPH_ELLIPSE, (5, 5))
        verification_code = cv2.morphologyEx(verification_code, cv2.MORPH_OPEN, kernel)
        show_img(verification_code)

    return verification_code


def img_ocr(img_name, fun=1):
    # 验证码识别400MB依赖包 pip install tensorflow>=1.14 numpy opencv-python pillow pyyaml
    # https://github.com/litongjava/muggle_ocr
    text = ""
    if fun == 1:
        pass
        # sdk = muggle_ocr.SDK(model_type=muggle_ocr.ModelType.OCR)
        # img = open(img_name, 'rb').read()
        # text = sdk.predict(image_bytes=img)
    else:
        # pip install baidu-aip chardet
        # https://ai.baidu.com/tech/ocr#百度ocr识别文字
        # https://console.bce.baidu.com/ai-engine/ocr/resource?apiId=27#每月1000次
        APP_ID = '115896386'
        API_KEY = 'BjvIG8O9uXLOXWGcpBB3CTZ6'
        SECRET_KEY = 'q7NLp5cZ4DzHGt057Sc3gUJ8ClKZ5snK'

        client = AipOcr(APP_ID, API_KEY, SECRET_KEY)
        img = open(f'{img_name}', 'rb').read()
        # 标准版
        result = client.basicGeneral(img)
        for i in result.get('words_result'):
            if text == "":
                text += (i.get('words'))
            else:
                print(f"识别的其他内容：{i.get('words')}")
        """
        # 高精度版
        msg = client.basicAccurate(image)
        # 通用文字识别（含位置信息版）
        msg = client.general(image)
        # 通用文字识别（含位置高精度版）
        msg = client.accurate(image)
        # 通用文字识别（含生僻字版）
        msg = client.enhancedGeneral(image)
        # 网络图片文字识别
        msg = client.webImage(image)
        # 如果提示{u'error_code': 17, u'error_msg': u'Open api daily request limit reached'}，百度识别每日有上限"""

    return text


def calculate(num1, num2, compute_sign=""):
    """正则判断符号后进行计算"""
    result = None
    try:
        num1 = int(num1)
        num2 = int(num2)
        if re.search(r"[/(<{!|]", compute_sign):
            result = num1 / num2
        elif re.search(r'[*×xX八]', compute_sign):
            result = num1 * num2
        elif re.search(r"[-一—~]", compute_sign):
            result = num1 - num2
        else:
            add = r"[+十]"
            result = num1 + num2
    except ValueError as e:
        print(f"转换出现错误：{e}")
    return result


# 使用正则表达式查找所有数字字符
# numbers = re.findall(ss, content)
def calculate_strategy(content):
    """验证码计算策略"""
    index = 0
    numbers = {}
    equal_sign_index = None
    for cont in content:
        m = re.search(r"\d", cont)
        if m:
            number = m.group()
            numbers[index] = number
        elif re.search(r"[=≈]", cont):
            equal_sign_index = index
        index += 1
    calculate_result = None

    keys = []
    for key in numbers.keys():
        keys.append(key)

    # 如果有等号（等号后退一位视为数字）
    if equal_sign_index and len(numbers) >= 2:
        if keys[0] + 1 == keys[1]:
            calculate_result = calculate(numbers[keys[0]], numbers[equal_sign_index - 1])
        else:
            calculate_result = calculate(numbers[keys[0]], numbers[equal_sign_index - 1], content[equal_sign_index - 2])
    # 只有两位数字
    elif len(numbers) >= 2:
        # 如果数字相邻（没有符号）
        if keys[0] + 1 == keys[1]:
            calculate_result = calculate(numbers[keys[0]], numbers[keys[1]])
        else:
            # keys[0] + 2 == keys[1]
            calculate_result = calculate(numbers[keys[0]], numbers[keys[1]], content[keys[1] - 1])
    return calculate_result


def auto_login(i=4 * 3):
    i -= 1
    filename = "code.png"
    uuid = fetch_and_save_image()
    if uuid:
        verification_code = image_grayscale(filename=filename, fun=1)
        # show_img(verification_code)
        # 二值化分割像素点
        # verification_code = image_binary(verification_code, thresh=60)
        # show_img(verification_code)
        # 补全像素点
        # verification_code = image_noise_reduction(verification_code, fun=3)
        # show_img(verification_code)
        # 保存灰度化的图片
        cv2.imwrite(filename=filename, img=verification_code)
        text = img_ocr(img_name=filename, fun=2)
        logging.debug(f"验证码文本：{text}")
        result = calculate_strategy(text)
        logging.debug(f"验证码结果：{result}")

        if result is None:
            if i < 0: return None  # 超过最大尝试次数时返回 None
            return auto_login(i)  # 递归调用时传递返回值
        login_json = login(uuid=uuid, code=result)
        logging.debug(f"登录结果：{login_json}")
        if login_json["code"] != 200:
            if i < 0: return None  # 超过最大尝试次数时返回 None
            logging.info(f"{i} {login_json}")
            return auto_login(i)  # 递归调用时传递返回值
        else:
            return login_json["data"]["access_token"]  # 成功时返回 access_token
    return None  # 当 uuid 为 None 时返回 None


def login(uuid, code):
    body = {"username": "admin", "password": "admin123", "code": code, "uuid": f"{uuid}"}
    response = session.request(method="post", url="http://192.168.50.202:9999/test-api/auth/login", headers=headers,
                               data=json.dumps(body), verify=True)
    return response.json()


session = requests.session()
headers = {"Content-Type": "application/json;charset=utf-8", "authorization": "Bearer "}


def fetch_and_save_image(img_name="code.png"):
    # 发送GET请求以获取base64编码的图像
    response = session.request(method="get", url="http://192.168.50.202:9999/test-api/code", headers=headers, data=None,
                               verify=True)
    if response.status_code == 200:
        res = response.json()
        img_base64 = res.get("img")
        # 对base64编码的图像进行解码
        img_data = base64.b64decode(img_base64)
        # 将解码后的图像写入文件 (e.g., image.png)
        with open(img_name, "wb") as file:
            file.write(img_data)
        return res.get("uuid")
    else:
        print(f"Failed to fetch the image. Status code: {response.text}")

    return None


def main():
    level = logging.getLogger().level
    # logging.getLogger().setLevel(logging.DEBUG)
    logging.getLogger().setLevel(logging.INFO)
    access_token = auto_login()
    if access_token:
        headers["authorization"] = f"Bearer {access_token}"
        logging.info(f"登录成功 {headers}")
        return headers
    else:
        logging.error("登录失败！")
    logging.getLogger().setLevel(level)
    return None


if __name__ == '__main__':
    main()
