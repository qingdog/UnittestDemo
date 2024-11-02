import asyncio
import json
import os

import aiofiles
import requests
from dotenv import load_dotenv

# 加载 .env 文件，任务每天早上 9 点触发执行
load_dotenv()
ACCOUNTS_JSON = "./accounts.json"


async def get_secrets_accounts():
    try:
        async with aiofiles.open(f'{ACCOUNTS_JSON}', mode='r', encoding='utf-8') as f:
            accounts_json = await f.read()
        accounts = json.loads(accounts_json)
    except Exception as e:
        print(f'读取 {ACCOUNTS_JSON} 文件时出错: {e}')
        return
    for account in accounts:
        os.environ['SMTP_SERVER'] = account['SMTP_SERVER']
        os.environ['SMTP_SSL'] = account['SMTP_SSL']
        os.environ['SMTP_EMAIL'] = account['SMTP_EMAIL']
        os.environ['SMTP_PASSWORD'] = account['SMTP_PASSWORD']
        os.environ['SMTP_NAME'] = account['SMTP_NAME']
        # 邮件标题兼容处理
        if os.environ['SMTP_NAME'] == "夸克登录失败（自己发送给自己）":
            os.environ['SMTP_NAME'] = "夸克自动登录脚本通知"


asyncio.run(get_secrets_accounts())

# 测试用环境变量
# os.environ['COOKIE_QUARK'] = ''

try:  # 异常捕捉
    from notify import send  # 导入消息通知模块
except Exception as err:  # 异常捕捉
    print('%s\n❌加载通知服务失败~' % err)
    pass

TELEGRAM_BOT_TOKEN = None
TELEGRAM_CHAT_ID = None


async def send_telegram_message(message):
    url = f"https://api.telegram.org/bot{TELEGRAM_BOT_TOKEN}/sendMessage"
    payload = {
        'chat_id': TELEGRAM_CHAT_ID,
        'text': message,
        'reply_markup': {
            'inline_keyboard': [
                [
                    {
                        'text': '问题反馈❓',
                        'url': 'https://t.me/yxjsjl'
                    }
                ]
            ]
        }
    }
    headers = {
        'Content-Type': 'application/json'
    }
    try:
        response = requests.post(url, json=payload, headers=headers)
        if response.status_code != 200:
            print(f"发送消息到Telegram失败: {response.text}")
    except Exception as e:
        print(f"发送消息到Telegram时出错: {e}")
