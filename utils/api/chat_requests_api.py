import asyncio
import json
import logging

import requests
import re
import logs.color_root_logger
from databases.aiomysql_client import AioMySQLClient


class Chat:
    session = requests.session()

    def completions(self, content="hello"):
        body = {"messages": [{"role": "system",
                              "content": "You are ChatGPT, a large language model trained by OpenAI.\nCarefully heed the user's instructions. \nRespond using Markdown."},
                             {"role": "user", "content": f"{content}"}], "model": "gpt-3.5-turbo", "temperature": 1,
                "presence_penalty": 0, "top_p": 1, "frequency_penalty": 0, "stream": True}
        header = {"authorization": "Bearer sk-",
                  "content-type": "application/json"}
        response = self.session.request(method="post", url="https://api.chatanywhere.com.cn/v1/chat/completions",
                                        headers=header, data=json.dumps(body), verify=False, stream=True)
        # response.encoding = response.apparent_encoding  # 解决乱码问题
        response.encoding = 'utf-8'  # 直接设置编码为UTF-8

        for line in response.iter_lines(chunk_size=1, decode_unicode=True):
            # 忽略空行
            if line:
                # 处理事件数据
                yield self.sse_to_json(line)
            else:
                # 空行可能是心跳，可以选择忽略或者处理
                pass

            # 检查连接是否关闭
            if response.raw.closed:
                break

    def sse_to_json(self, text):
        sse_prefix = "data: "
        result = text if re.search(f"^{sse_prefix}", text) is None else f"{text[len(sse_prefix):]}"
        if re.search("^{\"", result) is None:
            # logging.debug(result)
            return None
        return json.loads(result)


if __name__ == '__main__':
    def chat_content(content="你好！"):
        res = Chat().completions(content)
        rows = ""
        for row in res:
            if row is None:
                print(end="\n")
                continue
            if "choices" in row and len(row["choices"]) > 0 and "delta" in row["choices"][0] and "content" in \
                    row["choices"][0]["delta"]:
                content = row["choices"][0]["delta"]["content"]
                print(content, end="")
                rows += content
            elif "choices" in row and len(row["choices"]) > 0 and "delta" in row["choices"][0]:
                pass
            else:
                logs.color_root_logger.logger.warning(row)

        # logs.color_root_logger.logger.info(rows)

    async def get_origin_text(*arg):
        aiomysql_client = await AioMySQLClient().connect(user="liqi_cloud_test",password="G85BkJywwRxY5XBy",db="liqi_cloud_test")
        query_result: tuple = await aiomysql_client.execute_query(
            "select origin_text from lqc_extension_info where project_base_id = %s ", *arg)
        return query_result

    async def origin_handler():
        # res = await get_origin_text("1775462556439420929")
        res = await get_origin_text("1823192245796511745")
        # chat_content(f"请提取中文（只需要返回结果）：{res}")
        # 鸡肋
        chat_content(f"以下是政策原文：{res}。\n请从政策原文中提取 符合申报的条件信息。（保留换行以纯文本格式返回。注意：不需要markdown的格式返回也不要添加额外的文本）")

    AioMySQLClient.run(origin_handler)
