import base64
import json
import logging
import os
import re
import time
from datetime import datetime

import cv2
import numpy as np
import requests
from dotenv import set_key, load_dotenv

from utils import myutil
from utils.api import openai_api


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


def img_ocr(img_name, fun=2):
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
        import utils.api.ocr_baidu_api
        text = utils.api.ocr_baidu_api.baidu_orc_general_basic(img_name)
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


def calculate(num1, num2, operator=""):
    """正则判断符号后进行计算"""
    result = None
    try:
        num1 = int(num1)
        num2 = int(num2)
        if re.search(r"[+十M]", operator):
            result = num1 + num2
        elif re.search(r"[-一—~]", operator):
            result = num1 - num2
        elif re.search(r'[*×xX八]', operator):
            result = num1 * num2
        elif re.search(r"[/(\\、\[<{!|1]", operator):
            result = int(num1 / num2)
        else:
            # *乘号 和 /除号 难以识别
            result = num1 * num2
    except ValueError as e:
        print(f"转换出现错误，跳过：{e}")
    return result


# 使用正则表达式查找所有数字字符
# numbers = re.findall(ss, content)
def calculate_strategy(content):
    """验证码计算策略"""
    numbers = {}
    equal_sign_index = None
    # 遍历content，提取数字和等号位置
    for index, cont in enumerate(content):
        if mun := re.search(r"\d", cont):
            numbers[index] = mun.group()
        elif re.search(r"[=≈]", cont):
            equal_sign_index = index

    # 如果两个及以上的数字，无需计算
    if len(numbers) < 2: return None

    keys = list(numbers.keys())

    """if equal_sign_index:
        if keys[0] + 1 == keys[1]:
            calculate_result = calculate(numbers[keys[0]], numbers[equal_sign_index - 1])
        else:
            calculate_result = calculate(numbers[keys[0]], numbers[equal_sign_index - 1], content[equal_sign_index - 2])
    # 只有两位数字
    else:
        # 如果数字相邻（没有符号）
        if keys[0] + 1 == keys[1]:
            calculate_result = calculate(numbers[keys[0]], numbers[keys[1]])
        else:
            # keys[0] + 2 == keys[1]
            calculate_result = calculate(numbers[keys[0]], numbers[keys[1]], content[keys[1] - 1])"""
    if equal_sign_index and (equal_sign_index - 1) in numbers:
        # 等号前后的计算（如果等号后退一位为数字）
        first_num = numbers[keys[0]]
        second_num = numbers[equal_sign_index - 1]
        operator = content[equal_sign_index - 2] if keys[0] + 1 != equal_sign_index - 1 else ""
    else:
        # 只有两个数字时的计算
        first_num = numbers[keys[0]]
        second_num = numbers[keys[1]]
        # 如果数字不相邻，后退一位视为操作符
        operator = content[keys[1] - 1] if keys[0] + 1 != keys[1] else ""
    return calculate(first_num, second_num, operator)


def auto_login(i=4 * 3):
    """自动登录，失败则重试"""
    i -= 1
    filename = "code.png"
    uuid, img = fetch_and_save_image(img_name=filename)
    if uuid:
        if i >= 10:
            result = openai_text_recognition(img)
        else:
            result = text_recognition(filename)

        if result is None:
            if i < 0: return None  # 超过最大尝试次数时返回 None
            return auto_login(i)  # 递归调用时传递返回值
        login_json = login(uuid=uuid, code=result)
        if login_json["code"] != 200:
            logging.debug(f"登录失败：{login_json}")
            if i < 0: return None  # 超过最大尝试次数时返回 None
            logging.info(f"{i} {login_json}")
            return auto_login(i)  # 递归调用时传递返回值
        else:
            # 登录成功则删除保存的验证码图片
            if os.path.exists(filename):
                os.remove(filename)
            return login_json["data"]["access_token"]  # 成功时返回 access_token
    return None  # 当 uuid 为 None 时返回 None


def openai_text_recognition(img_base64_str):
    """使用大模型接口识别文字"""
    key = os.getenv("OPENAI_API_KEY")
    if key is not None and len(key) <= 3:
        key = os.getenv("OPENAI_API_KEY") + "6qdnd7aczJEwAFaCaItfz2JVft6bIXj9p7eKLLZiXMH1Bir1"[::-1]
    api_key = key
    content = ""

    # 记录开始时间
    start_time = time.time()
    # 调用生成器并流式处理结果
    # for chunk in stream_openai_response(messages, api_key=api_key):
    for chunk in openai_api.img_base64_to_openai("只需回答计算后的结果。", img_base64_str=img_base64_str,
                                                 api_key=api_key, stream=False):
        content += chunk
        print("验证码识别结果：", end='', flush=True)
        print(chunk, end='', flush=True)  # 实时打印接收到的每个块
    print(end='\n', flush=True)
    # 记录结束时间
    elapsed_time = time.time() - start_time
    logging.info(f"文本识别耗时：{elapsed_time}秒")

    return openai_api.get_chat_last_number(content)


def text_recognition(filename):
    """文本识别"""
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
    return result


def login(uuid, code, url="http://192.168.50.202:9999/test-api/auth/login"):
    body = {"username": "admin", "password": "admin123", "code": code, "uuid": f"{uuid}"}
    response = session.request(method="post", url=f"{url}", headers=headers,
                               data=json.dumps(body), verify=True)
    return response.json()


def fetch_and_save_image(img_name="code.png", url="http://192.168.50.202:9999/test-api/code"):
    # 发送GET请求以获取base64编码的图像
    response = session.request(method="get", url=f"{url}", headers=headers, data=None,
                               verify=True)
    if response.status_code == 200:
        res = response.json()
        img_base64 = res.get("img")
        # 对base64编码的图像进行解码
        img_data = base64.b64decode(img_base64)
        # 将解码后的图像写入文件 (e.g., image.png)
        with open(img_name, "wb") as file:
            file.write(img_data)
        return res.get("uuid"), res.get("img")
    else:
        print(f"获取图像失败.: {response.text}")

    return None


session = requests.session()
headers = {"Content-Type": "application/json;charset=utf-8"}


def login_verification_code():
    level = logging.getLogger().level
    if level > logging.INFO:
        # logging.getLogger().setLevel(logging.DEBUG)
        logging.getLogger().setLevel(logging.INFO)
    # access_token = auto_login()
    # 引入持久化功能
    access_token = login_save_token_with_expiry(auto_login)
    logging.debug(f"登录成功令牌：{access_token}")
    if access_token:
        return access_token
    else:
        logging.error("登录失败！")
    logging.getLogger().setLevel(level)
    session.close()
    return None


def login_save_token_with_expiry(login_func):
    """登录并保存带有过期时间的token
    :param login_func: 登录函数
    :return: token令牌 | 登录函数的返回值
    """
    login_token_key = "login_token"
    login_token_date_key = "login_token_date"
    token, last_date = os.getenv(login_token_key), os.getenv(login_token_date_key)
    current_date = datetime.now().strftime('%Y-%m-%d')

    # 如果没有 token 或者日期不同，则重新登录
    if token is None or last_date != current_date:
        token = login_func()
        # 重新加载 .env 文件到 os.environ
        os.environ[login_token_key] = set_key(os.path.join(myutil.get_project_path(), '.env'), login_token_key, token)[2]
        os.environ[login_token_date_key] = set_key(os.path.join(myutil.get_project_path(), '.env'), login_token_date_key, current_date)[2]
    return token


if __name__ == '__main__':
    load_dotenv()
    logging.getLogger().setLevel(logging.DEBUG)
    # text_recognition("4.png") # 识别
    login_verification_code()  # https://vue.ruoyi.vip/login?redirect=%2Findex
