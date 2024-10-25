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


def img_base64_to_openai(text, img_base64_str, api_key, img_type="image/png",
                         system_content="你是一个识别图片内容计算器。",
                         base_url=None, model="gpt-4o-mini"):
    client = OpenAI(
        api_key=api_key,
        base_url=base_url
    )
    stream = client.chat.completions.create(
        model=model,
        stream=True,
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
    for chunk in stream:
        yield chunk.choices[0].delta.content or ""


def get_chat_last_number(result):
    """从聊天记录中获取最后一个数字"""
    numbers = re.findall(r'\d+', result)
    last_number = None
    if numbers:
        last_number = numbers[-1]
    return last_number


def main():
    base_url = "https://open.bigmodel.cn/api/paas/v4/"
    api_key = ""
    model = "glm-4-flash"
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
    requests.get("https://demo.ruoyi.vip/captcha/captchaImage?type=math&s=0.39236748354325024")
    img_b64_str = "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"

    # 记录开始时间
    start_time = time.time()
    # 调用生成器并流式处理结果
    for chunk in stream_openai_response(messages, api_key=api_key, base_url=base_url, model=model):
        # for chunk in img_base64_to_openai("计算结果。", img_base64_str=img_b64_str, api_key=api_key, base_url=base_url, model=model):
        content += chunk
        print(chunk, end='', flush=True)  # 实时打印接收到的每个块
    # 记录结束时间
    elapsed_time = time.time() - start_time
    print(f"耗时：{elapsed_time}秒")

    ss = get_chat_last_number(content)
    print(ss)


if __name__ == '__main__':
    main()
