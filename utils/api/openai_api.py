import base64
import os
import re
import time

import requests
from dotenv import load_dotenv

load_dotenv()
from openai import OpenAI


def stream_openai_response(messages, api_key, model="gpt-4o-mini", base_url=None,
                           max_tokens=300):
    """
    调用 OpenAI API，并以生成器方式流式返回响应结果。

    参数:
    messages (list): 聊天消息列表，格式与 OpenAI API 相同。
    model (str): 使用的模型，默认为 gpt-4o。
    max_tokens (int): 生成响应的最大 token 数，默认 300。

    返回:
    generator: 逐步返回的响应内容。
    """
    client = OpenAI(
        # This is the default and can be omitted
        api_key=api_key,
        base_url=base_url,
    )

    # 逐步处理和返回响应的每一部分
    stream = client.chat.completions.create(
        model=model,
        messages=messages,
        stream=True,
        max_tokens=max_tokens
    )

    # img_type = "image/png"
    # img_b64_str = "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"
    # stream = client.chat.completions.create(
    #     model="gpt-4o-mini",
    #     stream=True,
    #     messages=[
    #         {
    #             "role": "user",
    #             "content": [
    #                 {"type": "text", "text": "计算结果"},
    #                 {
    #                     "type": "image_url",
    #                     "image_url": {"url": f"data:{img_type};base64,{img_b64_str}"},
    #                 },
    #             ],
    #         }
    #     ],
    # )

    for chunk in stream:
        yield chunk.choices[0].delta.content or ""  # 使用生成器逐步返回内容
    pass


def img_base64_to_openai(text, img_base64_str, system_content="你是一个识别图片内容并进行数学运算计算器，只需回答计算后的结果。",
                         base_url=None, api_key=None, stream=True, model="gpt-4o-mini", img_type="image/png"):
    client = OpenAI(
        api_key=api_key,
        base_url=base_url,
        timeout=10
    )
    completion = client.chat.completions.create(
        model=model,
        stream=stream,
        messages=[
            {"role": "system", "content": f"{system_content}"},
            {
                "role": "user",
                "content": [
                    {"type": "text", "text": f"{text}"},
                    {
                        "type": "image_url",
                        "image_url": {"url": f"data:{img_type};base64,{img_base64_str}"},
                    },
                ],
            }
        ],
    )
    if stream:
        for chunk in completion:
            yield chunk.choices[0].delta.content or ""
    else:
        yield completion.choices[0].message.content


def get_chat_last_number(result):
    """从聊天记录中获取最后一个数字"""
    numbers = re.findall(r'\d+', result)
    last_number = None
    if numbers:
        last_number = numbers[-1]
    return last_number


def main():
    # base_url = "https://open.bigmodel.cn/api/paas/v4/"
    api_key = os.getenv("OPENAI_API_KEY")
    # model = "glm-4-flash"
    # 示例调用生成器的方法
    img_url = "https://dashscope.oss-cn-beijing.aliyuncs.com/images/dog_and_girl.jpeg"
    messages = [
        {
            "role": "user",
            "content": [
                {"type": "text", "text": "图片里有什么？"},
                {
                    "type": "image_url",
                    "image_url": {"url": f"{img_url}"},
                },
            ]
        }
    ]
    # messages = [{"role": "user", "content": [{"type": "text", "text": "你好啊"}, ]}]

    content = ""
    from PIL import Image
    from io import BytesIO

    # 发送请求获取图片数据
    response = requests.get("https://demo.ruoyi.vip/captcha/captchaImage?type=math&s=0.39236748354325024")
    # 检查请求是否成功
    img_path = "captcha_image.png"
    if response.status_code == 200:
        # 将二进制数据转为图像并保存
        image = Image.open(BytesIO(response.content))
        image.save(img_path)  # 将图像保存为 PNG 格式
    else:
        print("无法获取图片")
    with open(img_path, "rb") as image_file:
        img_b64_str = base64.b64encode(image_file.read()).decode("utf-8")

    # 记录开始时间
    start_time = time.time()
    # 调用生成器并流式处理结果
    # for chunk in stream_openai_response(messages, api_key=api_key, base_url=base_url, model=model):
    for chunk in img_base64_to_openai("计算结果。", img_base64_str=img_b64_str, api_key=api_key):
        content += chunk
        print(chunk, end='', flush=True)  # 实时打印接收到的每个块
    # 记录结束时间
    elapsed_time = time.time() - start_time
    print(f"耗时：{elapsed_time}秒")

    ss = get_chat_last_number(content)
    print(ss)

    # 删除图片
    if os.path.exists(img_path):
        os.remove(img_path)


if __name__ == '__main__':
    main()
