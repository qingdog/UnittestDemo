#!/usr/bin/env python3
# _*_ coding:utf-8 _*_
import base64
import hashlib
import hmac
import json
import os
import re
import threading
import time
import urllib.parse
import smtplib
from concurrent.futures import ThreadPoolExecutor, Future
from email.mime.text import MIMEText
from email.header import Header
from email.utils import formataddr
from typing import Callable

import requests
from dotenv import load_dotenv

# 原先的 print 函数和主线程的锁
_print = print
mutual_exclusion = threading.Lock()


# 定义新的 print 函数
def print(text, *args, **kw):
    """使输出有序进行，不出现多线程同一时间输出导致错乱的问题。"""
    with mutual_exclusion:
        _print(text, *args, **kw)


def get_notify_function():
    """动态加载需要发送的通知"""
    return notify_function


notify_function: list[Callable] = []


# 通知服务
# fmt: off
class NotifyPushConfig:
    """读取环境变量或.env文件 覆盖push_config键值对"""
    CONSOLE = True  # 控制台输出
    HITOKOTO = False  # 启用一言（随机句子）
    SKIP_PUSH_TITLE = ''  # 根据标题跳过一些消息推送，环境变量： 用;分隔
    BARK_PUSH = '      '  # bark IP 或设备码，例：https://api.day.app/DxHcxxxxxRxxxxxxcm/#完整开源的 iOS APP，用来接收自定义推送
    BARK_ARCHIVE = '   '  # bark 推送是否存档
    BARK_GROUP = '     '  # bark 推送分组
    BARK_SOUND = '     '  # bark 推送声音
    BARK_ICON = '      '  # bark 推送图标
    BARK_LEVEL = '     '  # bark 推送时效性
    BARK_URL = '       '  # bark 推送跳转URL

    DD_BOT_SECRET = '  '  # 钉钉机器人的 DD_BOT_SECRET
    DD_BOT_TOKEN = '   '  # 钉钉机器人的 DD_BOT_TOKEN

    FSKEY = '          '  # 飞书机器人的 FSKEY

    GOBOT_URL = '      '  # go-cqhttp 发到qq号：http://127.0.0.1/send_private_msg、发送qq群：http://127.0.0.1/send_group_msg
    GOBOT_QQ = '       '  # go-cqhttp 发到qq号：user_id=个人QQ                     发送qq群填入：group_id=QQ的群
    GOBOT_TOKEN = '    '  # go-cqhttp 的 access_token

    GOTIFY_URL = '     '  # gotify地址如https://push.example.de:8080
    GOTIFY_TOKEN = '   '  # gotify的消息应用token
    GOTIFY_PRIORITY = 0  # 推送消息优先级默认为0

    IGOT_PUSH_KEY = '  '  # iGot 聚合推送的 IGOT_PUSH_KEY

    PUSH_KEY = '       '  # server 酱的 PUSH_KEY，兼容旧版与 Turbo 版

    DEER_KEY = '       '  # PushDeer 的 PUSHDEER_KEY
    DEER_URL = '       '  # PushDeer 的 PUSHDEER_URL

    CHAT_URL = '       '  # synology chat url
    CHAT_TOKEN = '     '  # synology chat token

    PUSH_PLUS_TOKEN = ''  # push+ 微信推送的用户令牌
    PUSH_PLUS_USER = ' '  # push+ 微信推送的群组编码

    QMSG_KEY = '       '  # qmsg 酱的 QMSG_KEY
    QMSG_TYPE = '      '  # qmsg 酱的 QMSG_TYPE

    QYWX_ORIGIN = '    '  # 企业微信代理地址

    QYWX_AM = '        '  # 企业微信应用

    QYWX_KEY = '       '  # 企业微信机器人

    TG_BOT_TOKEN = '   '  # tg 机器人的 TG_BOT_TOKEN，例：1407203283:AAG9rt-6RDaaX0HBLZQq0laNOh898iFYaRQ
    TG_USER_ID = '     '  # tg 机器人的 TG_USER_ID，例：1434078534
    TG_API_HOST = '    '  # tg 代理 api
    TG_PROXY_AUTH = '  '  # tg 代理认证参数
    TG_PROXY_HOST = '  '  # tg 机器人的 TG_PROXY_HOST
    TG_PROXY_PORT = '  '  # tg 机器人的 TG_PROXY_PORT

    AIBOTK_KEY = '     '  # 智能微秘书 个人中心的apikey 文档地址：http://wechat.aibotk.com/docs/about
    AIBOTK_TYPE = '    '  # 智能微秘书 发送目标 room 或 contact
    AIBOTK_NAME = '    '  # 智能微秘书  发送群名 或者好友昵称和type要对应好

    SMTP_SERVER = 'smtp.163.com:465'  # SMTP 发送邮件服务器，形如 smtp.qq.com:587
    SMTP_SSL = 'true'  # SMTP 发送邮件服务器是否使用 SSL，填写 true 或 false
    SMTP_EMAIL = '  '  # SMTP 收发件邮箱，通知将会由自己发给自己
    SMTP_PASSWORD = ''  # SMTP 登录密码，也可能为特殊口令，视具体邮件服务商说明而定
    SMTP_NAME = '测试通知'  # SMTP 收发件人姓名，可随意填写

    PUSHME_KEY = '     '  # PushMe 酱的 PUSHME_KEY

    CHRONOCAT_QQ = '   '  # qq号
    CHRONOCAT_TOKEN = ''  # CHRONOCAT 的token
    CHRONOCAT_URL = '  '  # CHRONOCAT的url地址

    WEBHOOK_URL = '    '  # 自定义通知 请求地址
    WEBHOOK_BODY = '   '  # 自定义通知 请求体
    WEBHOOK_HEADERS = ''  # 自定义通知 请求头
    WEBHOOK_METHOD = ' '  # 自定义通知 请求方法
    WEBHOOK_CONTENT_TYPE = ''  # 自定义通知 content-type

    def __init__(self):
        """加载通知模块时需进行配置。在发送通知之前只需执行一次。"""
        # 首先读取 面板变量 或者 Github Action 运行变量
        load_dotenv()
        for attr, value in NotifyPushConfig.__dict__.items():
            if attr.startswith('__'): continue
            env_value = os.getenv(attr)
            if env_value is not None:
                setattr(self, attr, env_value)  # 保留原始配置在未设置值 (None)跳过。即：支持空串设置
            elif isinstance(value, str):
                setattr(self, attr, value.rstrip())  # 去除字符串格式的前后空格

        if self.BARK_PUSH: notify_function.append(bark)
        if self.CONSOLE: notify_function.append(console_print)
        if self.DD_BOT_TOKEN and self.DD_BOT_SECRET: notify_function.append(dingding_bot)
        if self.FSKEY: notify_function.append(feishu_bot)
        if self.GOBOT_URL and self.GOBOT_QQ: notify_function.append(go_cqhttp)
        if self.GOTIFY_URL and self.GOTIFY_TOKEN: notify_function.append(gotify)
        if self.IGOT_PUSH_KEY: notify_function.append(iGot)
        if self.PUSH_KEY: notify_function.append(serverJ)
        if self.DEER_KEY: notify_function.append(pushdeer)
        if self.CHAT_URL and self.CHAT_TOKEN: notify_function.append(chat)
        if self.PUSH_PLUS_TOKEN: notify_function.append(pushplus_bot)
        if self.QMSG_KEY and self.QMSG_TYPE: notify_function.append(qmsg_bot)
        if self.QYWX_AM: notify_function.append(wecom_app)
        if self.QYWX_KEY: notify_function.append(wecom_bot)
        if self.TG_BOT_TOKEN and self.TG_USER_ID: notify_function.append(telegram_bot)
        if self.AIBOTK_KEY and self.AIBOTK_TYPE and self.AIBOTK_NAME: notify_function.append(aibotk)
        if (self.SMTP_SERVER and self.SMTP_SSL and self.SMTP_EMAIL
                and self.SMTP_PASSWORD and self.SMTP_NAME): notify_function.append(smtp)
        if self.PUSHME_KEY: notify_function.append(pushme)
        if self.CHRONOCAT_URL and self.CHRONOCAT_QQ and self.CHRONOCAT_TOKEN: notify_function.append(chronocat)
        if self.WEBHOOK_URL and self.WEBHOOK_METHOD: notify_function.append(custom_notify)


# fmt: on

def bark(title: str, content: str, push_config: NotifyPushConfig) -> None:
    """
    使用 bark 推送消息。
    """
    if not push_config.BARK_PUSH:
        print("bark 服务的 BARK_PUSH 未设置!!\n取消推送")
        return
    print("bark 服务启动")

    if push_config.BARK_PUSH.startswith("http"):
        url = f'{push_config.BARK_PUSH}/{urllib.parse.quote_plus(title)}/{urllib.parse.quote_plus(content)}'
    else:
        url = f'https://api.day.app/{push_config.BARK_PUSH}/{urllib.parse.quote_plus(title)}/{urllib.parse.quote_plus(content)}'

    bark_params = {
        "BARK_ARCHIVE": "isArchive",
        "BARK_GROUP": "group",
        "BARK_SOUND": "sound",
        "BARK_ICON": "icon",
        "BARK_LEVEL": "level",
        "BARK_URL": "url",
    }
    params = ""
    for pair in filter(
            # 筛选出所有键以 "BARK_" 开头、键不等于 "BARK_PUSH"、值非空并且 bark_params 中有对应的键。
            lambda pairs: pairs[0].startswith("BARK_") and pairs[0] != "BARK_PUSH" and pairs[1] and bark_params.get(pairs[0]),
            push_config.__dict__.items(), ):
        params += f"{bark_params.get(pair[0])}={pair[1]}&"
    if params:
        url = url + "?" + params.rstrip("&")
    response = requests.get(url).json()

    if response["code"] == 200:
        print("bark 推送成功！")
    else:
        print("bark 推送失败！")


def console_print(title: str, content: str, push_config: NotifyPushConfig):
    """使用 控制台 推送消息。"""
    print(f"{title}\n{content}")
    return f"使用 控制台 推送消息成功..."


def dingding_bot(title: str, content: str, push_config: NotifyPushConfig) -> None:
    """
    使用 钉钉机器人 推送消息。
    """
    if not push_config.DD_BOT_SECRET or not push_config.DD_BOT_TOKEN:
        print("钉钉机器人 服务的 DD_BOT_SECRET 或者 DD_BOT_TOKEN 未设置!!\n取消推送")
        return
    print("钉钉机器人 服务启动")

    timestamp = str(round(time.time() * 1000))
    secret_enc = push_config.DD_BOT_SECRET.encode("utf-8")
    string_to_sign = "{}\n{}".format(timestamp, push_config.DD_BOT_SECRET)
    string_to_sign_enc = string_to_sign.encode("utf-8")
    hmac_code = hmac.new(
        secret_enc, string_to_sign_enc, digestmod=hashlib.sha256
    ).digest()
    sign = urllib.parse.quote_plus(base64.b64encode(hmac_code))
    url = f'https://oapi.dingtalk.com/robot/send?access_token={push_config.DD_BOT_TOKEN}&timestamp={timestamp}&sign={sign}'
    headers = {"Content-Type": "application/json;charset=utf-8"}
    data = {"msgtype": "text", "text": {"content": f"{title}\n\n{content}"}}
    response = requests.post(
        url=url, data=json.dumps(data), headers=headers, timeout=15
    ).json()

    if not response["errcode"]:
        print("钉钉机器人 推送成功！")
    else:
        print("钉钉机器人 推送失败！")


def feishu_bot(title: str, content: str, push_config: NotifyPushConfig) -> None:
    """
    使用 飞书机器人 推送消息。
    """
    if not push_config.FSKEY:
        print("飞书 服务的 FSKEY 未设置!!\n取消推送")
        return
    print("飞书 服务启动")

    url = f'https://open.feishu.cn/open-apis/bot/v2/hook/{push_config.FSKEY}'
    data = {"msg_type": "text", "content": {"text": f"{title}\n\n{content}"}}
    response = requests.post(url, data=json.dumps(data)).json()

    if response.get("StatusCode") == 0:
        print("飞书 推送成功！")
    else:
        print("飞书 推送失败！错误信息如下：\n", response)


def go_cqhttp(title: str, content: str, push_config: NotifyPushConfig) -> None:
    """
    使用 go_cqhttp 推送消息。
    """
    if not push_config.GOBOT_URL or not push_config.GOBOT_QQ:
        print("go-cqhttp 服务的 GOBOT_URL 或 GOBOT_QQ 未设置!!\n取消推送")
        return
    print("go-cqhttp 服务启动")

    url = f'{push_config.GOBOT_URL}?access_token={push_config.GOBOT_TOKEN}&{push_config.GOBOT_QQ}&message=标题:{title}\n内容:{content}'
    response = requests.get(url).json()

    if response["status"] == "ok":
        print("go-cqhttp 推送成功！")
    else:
        print("go-cqhttp 推送失败！")


def gotify(title: str, content: str, push_config: NotifyPushConfig) -> None:
    """
    使用 gotify 推送消息。
    """
    if not push_config.GOTIFY_URL or not push_config.GOTIFY_TOKEN:
        print("gotify 服务的 GOTIFY_URL 或 GOTIFY_TOKEN 未设置!!\n取消推送")
        return
    print("gotify 服务启动")

    url = f'{push_config.GOTIFY_URL}/message?token={push_config.GOTIFY_TOKEN}'
    data = {
        "title": title,
        "message": content,
        "priority": push_config.GOTIFY_PRIORITY,
    }
    response = requests.post(url, data=data).json()

    if response.get("id"):
        print("gotify 推送成功！")
    else:
        print("gotify 推送失败！")


def iGot(title: str, content: str, push_config: NotifyPushConfig) -> None:
    """
    使用 iGot 推送消息。
    """
    if not push_config.IGOT_PUSH_KEY:
        print("iGot 服务的 IGOT_PUSH_KEY 未设置!!\n取消推送")
        return
    print("iGot 服务启动")

    url = f'https://push.hellyw.com/{push_config.IGOT_PUSH_KEY}'
    data = {"title": title, "content": content}
    headers = {"Content-Type": "application/x-www-form-urlencoded"}
    response = requests.post(url, data=data, headers=headers).json()

    if response["ret"] == 0:
        print("iGot 推送成功！")
    else:
        print(f'iGot 推送失败！{response["errMsg"]}')


def serverJ(title: str, content: str, push_config: NotifyPushConfig) -> None:
    """
    通过 serverJ 推送消息。
    """
    if not push_config.PUSH_KEY:
        print("serverJ 服务的 PUSH_KEY 未设置!!\n取消推送")
        return
    print("serverJ 服务启动")

    data = {"text": title, "desp": content.replace("\n", "\n\n")}
    if push_config.PUSH_KEY.find("SCT") != -1:
        url = f'https://sctapi.ftqq.com/{push_config.PUSH_KEY}.send'
    else:
        url = f'https://sc.ftqq.com/{push_config.PUSH_KEY}.send'
    response = requests.post(url, data=data).json()

    if response.get("errno") == 0 or response.get("code") == 0:
        print("serverJ 推送成功！")
    else:
        print(f'serverJ 推送失败！错误码：{response["message"]}')


def pushdeer(title: str, content: str, push_config: NotifyPushConfig) -> None:
    """
    通过PushDeer 推送消息
    """
    if not push_config.DEER_KEY:
        print("PushDeer 服务的 DEER_KEY 未设置!!\n取消推送")
        return
    print("PushDeer 服务启动")
    data = {
        "text": title,
        "desp": content,
        "type": "markdown",
        "pushkey": push_config.DEER_KEY,
    }
    url = "https://api2.pushdeer.com/message/push"
    if push_config.DEER_URL:
        url = push_config.DEER_URL

    response = requests.post(url, data=data).json()

    if len(response.get("content").get("result")) > 0:
        print("PushDeer 推送成功！")
    else:
        print("PushDeer 推送失败！错误信息：", response)


def chat(title: str, content: str, push_config: NotifyPushConfig) -> None:
    """
    通过Chat 推送消息
    """
    if not push_config.CHAT_URL or not push_config.CHAT_TOKEN:
        print("chat 服务的 CHAT_URL或CHAT_TOKEN 未设置!!\n取消推送")
        return
    print("chat 服务启动")
    data = "payload=" + json.dumps({"text": title + "\n" + content})
    url = push_config.CHAT_URL + push_config.CHAT_TOKEN
    response = requests.post(url, data=data)

    if response.status_code == 200:
        print("Chat 推送成功！")
    else:
        print("Chat 推送失败！错误信息：", response)


def pushplus_bot(title: str, content: str, push_config: NotifyPushConfig) -> None:
    """
    通过 push+ 推送消息。
    """
    if not push_config.PUSH_PLUS_TOKEN:
        print("PUSHPLUS 服务的 PUSH_PLUS_TOKEN 未设置!!\n取消推送")
        return
    print("PUSHPLUS 服务启动")

    url = "http://www.pushplus.plus/send"
    data = {
        "token": push_config.PUSH_PLUS_TOKEN,
        "title": title,
        "content": content,
        "topic": push_config.PUSH_PLUS_USER,
    }
    body = json.dumps(data).encode(encoding="utf-8")
    headers = {"Content-Type": "application/json"}
    response = requests.post(url=url, data=body, headers=headers).json()

    if response["code"] == 200:
        print("PUSHPLUS 推送成功！")

    else:
        url_old = "http://pushplus.hxtrip.com/send"
        headers["Accept"] = "application/json"
        response = requests.post(url=url_old, data=body, headers=headers).json()

        if response["code"] == 200:
            print("PUSHPLUS(hxtrip) 推送成功！")

        else:
            print("PUSHPLUS 推送失败！")


def qmsg_bot(title: str, content: str, push_config: NotifyPushConfig) -> None:
    """
    使用 qmsg 推送消息。
    """
    if not push_config.QMSG_KEY or not push_config.QMSG_TYPE:
        print("qmsg 的 QMSG_KEY 或者 QMSG_TYPE 未设置!!\n取消推送")
        return
    print("qmsg 服务启动")

    url = f'https://qmsg.zendee.cn/{push_config.QMSG_TYPE}/{push_config.QMSG_KEY}'
    payload = {"msg": f'{title}\n\n{content.replace("----", "-")}'.encode("utf-8")}
    response = requests.post(url=url, params=payload).json()

    if response["code"] == 0:
        print("qmsg 推送成功！")
    else:
        print(f'qmsg 推送失败！{response["reason"]}')


def wecom_app(title: str, content: str, push_config: NotifyPushConfig) -> None:
    """
    通过 企业微信 APP 推送消息。
    """
    if not push_config.QYWX_AM:
        print("QYWX_AM 未设置!!\n取消推送")
        return
    QYWX_AM_AY = re.split(",", push_config.QYWX_AM)
    if 4 < len(QYWX_AM_AY) > 5:
        print("QYWX_AM 设置错误!!\n取消推送")
        return
    print("企业微信 APP 服务启动")

    corpid = QYWX_AM_AY[0]
    corpsecret = QYWX_AM_AY[1]
    touser = QYWX_AM_AY[2]
    agentid = QYWX_AM_AY[3]
    try:
        media_id = QYWX_AM_AY[4]
    except IndexError:
        media_id = ""
    wx = WeCom(corpid, corpsecret, agentid)
    # 如果没有配置 media_id 默认就以 text 方式发送
    if not media_id:
        message = title + "\n\n" + content
        response = wx.send_text(message, touser)
    else:
        response = wx.send_mpnews(title, content, media_id, touser)

    if response == "ok":
        print("企业微信推送成功！")
    else:
        print("企业微信推送失败！错误信息如下：\n", response)


class WeCom:
    def __init__(self, corpid, corpsecret, agentid):
        self.CORPID = corpid
        self.CORPSECRET = corpsecret
        self.AGENTID = agentid
        self.ORIGIN = "https://qyapi.weixin.qq.com"
        if notify_push_config.QYWX_ORIGIN:
            self.ORIGIN = notify_push_config.QYWX_ORIGIN

    def get_access_token(self):
        url = f"{self.ORIGIN}/cgi-bin/gettoken"
        values = {
            "corpid": self.CORPID,
            "corpsecret": self.CORPSECRET,
        }
        req = requests.post(url, params=values)
        data = json.loads(req.text)
        return data["access_token"]

    def send_text(self, message, touser="@all"):
        send_url = (
            f"{self.ORIGIN}/cgi-bin/message/send?access_token={self.get_access_token()}"
        )
        send_values = {
            "touser": touser,
            "msgtype": "text",
            "agentid": self.AGENTID,
            "text": {"content": message},
            "safe": "0",
        }
        send_msges = bytes(json.dumps(send_values), "utf-8")
        respone = requests.post(send_url, send_msges)
        respone = respone.json()
        return respone["errmsg"]

    def send_mpnews(self, title, message, media_id, touser="@all"):
        send_url = (
            f"{self.ORIGIN}/cgi-bin/message/send?access_token={self.get_access_token()}"
        )
        send_values = {
            "touser": touser,
            "msgtype": "mpnews",
            "agentid": self.AGENTID,
            "mpnews": {
                "articles": [
                    {
                        "title": title,
                        "thumb_media_id": media_id,
                        "author": "Author",
                        "content_source_url": "",
                        "content": message.replace("\n", "<br/>"),
                        "digest": message,
                    }
                ]
            },
        }
        send_msges = bytes(json.dumps(send_values), "utf-8")
        respone = requests.post(send_url, send_msges)
        respone = respone.json()
        return respone["errmsg"]


def wecom_bot(title: str, content: str, push_config: NotifyPushConfig) -> None:
    """
    通过 企业微信机器人 推送消息。
    """
    if not push_config.QYWX_KEY:
        print("企业微信机器人 服务的 QYWX_KEY 未设置!!\n取消推送")
        return
    print("企业微信机器人服务启动")

    origin = "https://qyapi.weixin.qq.com"
    if push_config.QYWX_ORIGIN:
        origin = push_config.QYWX_ORIGIN

    url = f"{origin}/cgi-bin/webhook/send?key={push_config.QYWX_KEY}"
    headers = {"Content-Type": "application/json;charset=utf-8"}
    data = {"msgtype": "text", "text": {"content": f"{title}\n\n{content}"}}
    response = requests.post(
        url=url, data=json.dumps(data), headers=headers, timeout=15
    ).json()

    if response["errcode"] == 0:
        print("企业微信机器人推送成功！")
    else:
        print("企业微信机器人推送失败！")


def telegram_bot(title: str, content: str, push_config: NotifyPushConfig) -> None:
    """
    使用 telegram 机器人 推送消息。
    """
    if not push_config.TG_BOT_TOKEN or not push_config.TG_USER_ID:
        print("tg 服务的 bot_token 或者 user_id 未设置!!\n取消推送")
        return
    print("tg 服务启动")

    if push_config.TG_API_HOST:
        url = f"https://{push_config.TG_API_HOST}/bot{push_config.TG_BOT_TOKEN}/sendMessage"
    else:
        url = (
            f"https://api.telegram.org/bot{push_config.TG_BOT_TOKEN}/sendMessage"
        )
    headers = {"Content-Type": "application/x-www-form-urlencoded"}
    payload = {
        "chat_id": str(push_config.TG_USER_ID),
        "text": f"{title}\n\n{content}",
        "disable_web_page_preview": "true",
    }
    proxies = None
    if push_config.TG_PROXY_HOST and push_config.TG_PROXY_PORT:
        if push_config.TG_PROXY_AUTH is not None and "@" not in push_config.TG_PROXY_HOST:
            push_config.TG_PROXY_HOST = (push_config.TG_PROXY_AUTH + "@" + push_config.TG_PROXY_HOST)
        proxy_str = "http://{}:{}".format(push_config.TG_PROXY_HOST, push_config.TG_PROXY_PORT)
        proxies = {"http": proxy_str, "https": proxy_str}
    response = requests.post(
        url=url, headers=headers, params=payload, proxies=proxies
    ).json()

    if response["ok"]:
        print("tg 推送成功！")
    else:
        print("tg 推送失败！")


def aibotk(title: str, content: str, push_config: NotifyPushConfig) -> None:
    """
    使用 智能微秘书 推送消息。
    """
    if (
            not push_config.AIBOTK_KEY
            or not push_config.AIBOTK_TYPE
            or not push_config.AIBOTK_NAME
    ):
        print("智能微秘书 的 AIBOTK_KEY 或者 AIBOTK_TYPE 或者 AIBOTK_NAME 未设置!!\n取消推送")
        return
    print("智能微秘书 服务启动")

    if push_config.AIBOTK_TYPE == "room":
        url = "https://api-bot.aibotk.com/openapi/v1/chat/room"
        data = {
            "apiKey": push_config.AIBOTK_KEY,
            "roomName": push_config.AIBOTK_NAME,
            "message": {"type": 1, "content": f"【青龙快讯】\n\n{title}\n{content}"},
        }
    else:
        url = "https://api-bot.aibotk.com/openapi/v1/chat/contact"
        data = {
            "apiKey": push_config.AIBOTK_KEY,
            "name": push_config.AIBOTK_NAME,
            "message": {"type": 1, "content": f"【青龙快讯】\n\n{title}\n{content}"},
        }
    body = json.dumps(data).encode(encoding="utf-8")
    headers = {"Content-Type": "application/json"}
    response = requests.post(url=url, data=body, headers=headers).json()
    print(response)
    if response["code"] == 0:
        print("智能微秘书 推送成功！")
    else:
        print(f'智能微秘书 推送失败！{response["error"]}')


def smtp(title: str, content: str, push_config: NotifyPushConfig) -> None:
    """使用 SMTP 邮件 推送消息。"""
    if not push_config.SMTP_SERVER or not push_config.SMTP_SSL or not push_config.SMTP_EMAIL or not push_config.SMTP_PASSWORD or not push_config.SMTP_NAME:
        print("SMTP 邮件 的 SMTP_SERVER 或者 SMTP_SSL 或者 SMTP_EMAIL 或者 SMTP_PASSWORD 或者 SMTP_NAME 未设置!!\n取消推送")
        return
    print("SMTP 邮件 服务启动")

    message = MIMEText(content, "plain", "utf-8")
    message["From"] = formataddr((Header(push_config.SMTP_NAME, "utf-8").encode(), push_config.SMTP_EMAIL,))
    message["To"] = formataddr((Header(push_config.SMTP_NAME, "utf-8").encode(), push_config.SMTP_EMAIL,))
    message["Subject"] = Header(title, "utf-8")

    try:
        smtp_server = (smtplib.SMTP_SSL(push_config.SMTP_SERVER) if push_config.SMTP_SSL == "true" else smtplib.SMTP(push_config.SMTP_SERVER))
        smtp_server.login(push_config.SMTP_EMAIL, push_config.SMTP_PASSWORD)
        smtp_server.sendmail(push_config.SMTP_EMAIL, push_config.SMTP_EMAIL, message.as_bytes(), )
        smtp_server.close()
        print("SMTP 邮件 推送成功！")
    except Exception as e:
        print(f"SMTP 邮件 推送失败！{e}")


def pushme(title: str, content: str, push_config: NotifyPushConfig) -> None:
    """
    使用 PushMe 推送消息。
    """
    if not push_config.PUSHME_KEY:
        print("PushMe 服务的 PUSHME_KEY 未设置!!\n取消推送")
        return
    print("PushMe 服务启动")

    url = f'https://push.i-i.me/?push_key={push_config.PUSHME_KEY}'
    data = {
        "title": title,
        "content": content,
    }
    response = requests.post(url, data=data)

    if response.status_code == 200 and response.text == "success":
        print("PushMe 推送成功！")
    else:
        print(f"PushMe 推送失败！{response.status_code} {response.text}")


def chronocat(title: str, content: str, push_config: NotifyPushConfig) -> None:
    """
    使用 CHRONOCAT 推送消息。
    """
    if (
            not push_config.CHRONOCAT_URL
            or not push_config.CHRONOCAT_QQ
            or not push_config.CHRONOCAT_TOKEN
    ):
        print("CHRONOCAT 服务的 CHRONOCAT_URL 或 CHRONOCAT_QQ 未设置!!\n取消推送")
        return

    print("CHRONOCAT 服务启动")

    user_ids = re.findall(r"user_id=(\d+)", push_config.CHRONOCAT_QQ)
    group_ids = re.findall(r"group_id=(\d+)", push_config.CHRONOCAT_QQ)

    url = f'{push_config.CHRONOCAT_URL}/api/message/send'
    headers = {
        "Content-Type": "application/json",
        "Authorization": f'Bearer {push_config.CHRONOCAT_TOKEN}',
    }

    for chat_type, ids in [(1, user_ids), (2, group_ids)]:
        if not ids:
            continue
        for chat_id in ids:
            data = {
                "peer": {"chatType": chat_type, "peerUin": chat_id},
                "elements": [
                    {
                        "elementType": 1,
                        "textElement": {"content": f"{title}\n\n{content}"},
                    }
                ],
            }
            response = requests.post(url, headers=headers, data=json.dumps(data))
            if response.status_code == 200:
                if chat_type == 1:
                    print(f"QQ个人消息:{ids}推送成功！")
                else:
                    print(f"QQ群消息:{ids}推送成功！")
            else:
                if chat_type == 1:
                    print(f"QQ个人消息:{ids}推送失败！")
                else:
                    print(f"QQ群消息:{ids}推送失败！")


def parse_headers(headers):
    if not headers:
        return {}

    parsed = {}
    lines = headers.split("\n")

    for line in lines:
        i = line.find(":")
        if i == -1:
            continue

        key = line[:i].strip().lower()
        val = line[i + 1:].strip()
        parsed[key] = parsed.get(key, "") + ", " + val if key in parsed else val

    return parsed


def parse_body(body, content_type):
    if not body:
        return ""

    parsed = {}
    lines = body.split("\n")

    for line in lines:
        i = line.find(":")
        if i == -1:
            continue

        key = line[:i].strip().lower()
        val = line[i + 1:].strip()

        if not key or key in parsed:
            continue

        try:
            json_value = json.loads(val)
            parsed[key] = json_value
        except:
            parsed[key] = val

    if content_type == "application/x-www-form-urlencoded":
        data = urllib.parse.urlencode(parsed, doseq=True)
        return data

    if content_type == "application/json":
        data = json.dumps(parsed)
        return data

    return parsed


def format_notify_content(url, body, title, content):
    if "$title" not in url and "$title" not in body:
        return {}

    formatted_url = url.replace("$title", urllib.parse.quote_plus(title)).replace(
        "$content", urllib.parse.quote_plus(content)
    )
    formatted_body = body.replace("$title", title).replace("$content", content)

    return formatted_url, formatted_body


def custom_notify(title: str, content: str, push_config: NotifyPushConfig) -> None:
    """
    通过 自定义通知 推送消息。
    """
    if not push_config.WEBHOOK_URL or not push_config.WEBHOOK_METHOD:
        print("自定义通知的 WEBHOOK_URL 或 WEBHOOK_METHOD 未设置!!\n取消推送")
        return

    print("自定义通知服务启动")

    WEBHOOK_URL = push_config.WEBHOOK_URL
    WEBHOOK_METHOD = push_config.WEBHOOK_METHOD
    WEBHOOK_CONTENT_TYPE = push_config.WEBHOOK_CONTENT_TYPE
    WEBHOOK_BODY = push_config.WEBHOOK_BODY
    WEBHOOK_HEADERS = push_config.WEBHOOK_HEADERS

    formatUrl, formatBody = format_notify_content(
        WEBHOOK_URL, WEBHOOK_BODY, title, content
    )

    if not formatUrl and not formatBody:
        print("请求头或者请求体中必须包含 $title 和 $content")
        return

    headers = parse_headers(WEBHOOK_HEADERS)
    body = parse_body(formatBody, WEBHOOK_CONTENT_TYPE)
    response = requests.request(
        method=WEBHOOK_METHOD, url=formatUrl, headers=headers, timeout=15, data=body
    )

    if response.status_code == 200:
        print("自定义通知推送成功！")
    else:
        print(f"自定义通知推送失败！{response.status_code} {response.text}")


def get_hitokoto() -> str:
    """获取一条一言。"""
    url = "https://v1.hitokoto.cn/"
    res = requests.get(url).json()
    return res["hitokoto"] + "    ----" + res["from"]


notify_push_config = NotifyPushConfig()  # 文件中直接执行通知配置函数


def send_before_rule(title, content):
    # 根据标题跳过一些消息推送，环境变量：SKIP_PUSH_TITLE 用;分隔
    skip_title = notify_push_config.SKIP_PUSH_TITLE
    if skip_title and title in re.split(";", skip_title):
        print(f"{title} 在SKIP_PUSH_TITLE环境变量内，跳过推送！")
        return

    if notify_push_config.HITOKOTO:
        hitokoto = get_hitokoto()
        if hitokoto: content += "\n" + hitokoto
    return content


def send(title: str, content="") -> list[Future]:
    """发送通知"""
    content = send_before_rule(title, content)
    '''threads = []# 创建线程并启动
    result_queue = queue.Queue()  # 创建一个队列来接收返回值
    for notify_task in get_notify_function():
        t = threading.Thread(target=notify_task, args=(title, content, ), name=notify_task.__name__)
        threads.append(t)
        t.start()
    for t in threads: t.join()# 等待所有线程结束'''
    futures: list[Future] = []
    with ThreadPoolExecutor() as executor:
        # 提交任务并获取 future 对象
        for notify_task in get_notify_function():
            future = executor.submit(notify_task, title, content, notify_push_config)
            futures.append(future)
    return futures


def main():
    notify_push_config.HITOKOTO = "1"
    return send("title", "content")


if __name__ == "__main__":
    fus = main()
    for ff in fus: print(ff.result())
