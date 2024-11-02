import json
import asyncio
import logging
import platform
import re
import subprocess
import os
import random
import time
from datetime import datetime, timedelta, timezone

from pyppeteer import launch
from pyppeteer.page import Page  # 导入 Page 类型
from dotenv import load_dotenv

import utils.verification_code_login

load_dotenv()
# 环境变量
PIG_URL = os.getenv('PIG_URL')
PIG_USERNAME = os.getenv('PIG_USERNAME')
PIG_PASSWORD = os.getenv('PIG_PASSWORD')

OS_NAME = platform.system()


def find_chrome_path():
    """查找 Chrome 浏览器路径（Linux）"""
    if OS_NAME == "Windows":
        win_browser_path = get_win_browser_path()
        if len(win_browser_path) > 0:
            return get_win_browser_path()[0]
    else:
        try:
            path = subprocess.check_output(['which', 'google-chrome']).decode().strip()
            return path
        except subprocess.CalledProcessError:
            pass
    return None


def get_win_browser_path(path="C:", file_list=[],
                         program_name=r"(?i)chrome\.exe$", program_dir=r"(?i)program|google|users"):
    try:
        os.listdir(path)
    except Exception:
        return
    for i in os.listdir(path):
        path1 = os.path.join(path, i)
        if os.path.isdir(path1) and re.search(program_dir, path1):
            get_win_browser_path(path1, file_list)
        elif os.path.isfile(path1):
            if re.search(program_name, path1):
                file_list.append(path1.replace('\\\\', '\\'))
                return file_list
    return file_list


# Pyppeteer 也可以用来控制 Chrome 浏览器，但与它捆绑的 Chromium 版本配合最佳。无法保证它与其他版本兼容。请谨慎使用 executablePath 选项
chrome_executable_path = find_chrome_path()
chrome_startup_args = ['--window-size=1800,900']  # 最大化启动--start-maximized
is_headless = OS_NAME != "Windows"  # 非windows则以无头模式启动
chrome_startup_args.append("--disable-infobars")  # 禁用信息栏
if is_headless:
    chrome_startup_args.append("--disable-gpu")  # 兼容谷歌文档
    chrome_startup_args.append("--no-sandbox")  # 沙箱模式
    chrome_startup_args.append("--disable-setuid-sandbox")


async def chrome_init():
    """初始化 Chrome 浏览器并返回页面实例"""
    print(f"start '{chrome_executable_path}' # starting...")
    browser = await launch(headless=is_headless, args=chrome_startup_args, executablePath=chrome_executable_path,
                           ignoreHTTPSErrors=True, ignoreDefaultArgs=['--enable-automation'], autoclose=True)
    # page = browser.newPage()
    page = (await browser.pages())[0]
    # 设置页面尺寸为最大化状态
    await page.setViewport({"width": 1920, "height": 1080})
    page.setDefaultNavigationTimeout(180000)  # 3 分钟
    # await asyncio.sleep(random.randint(500, 1000) / 1000)  # 等待 0.5 到 1 秒
    return browser, page


async def login_pig(page, username, password, url):
    """登录并返回是否登录成功"""
    try:
        """
        username_input = await page.querySelector('#email')
        if username_input:
            # 在浏览器页面的上下文中执行 JavaScript 操作 username_input 作为参数传入清空输入框
            await page.evaluate('''(input) => input.value = "";''', username_input)"""
        await page.goto(f'https://{url}/auth/login')
        await page.type('#email', username)
        await page.type('#passwd', password)
        await page.click('#login')
        await page.waitForNavigation()

        is_logged_in = await page.evaluate('''() => document.querySelector("a[href='/user/logout']") != null''')
        if is_logged_in:
            checkin_button = await page.querySelector('button#checkin')
            if checkin_button:
                await checkin_button.click()
                await asyncio.sleep(3.5)
                element = await page.querySelector('#msg')
                checkin_text = await page.evaluate('(element) => element.innerText', element)
                print(checkin_text)
                # 确定 document.querySelector("#checkin-btn").innerText
            else:
                logging.warning("无法找到签到按钮：page.querySelector('button#checkin')")
                history_text = await page.evaluate(
                    '() => document.querySelectorAll("div.card-inner.margin-bottom-no")[1].innerText')
                print(history_text)
        return is_logged_in

    except Exception as e:
        print(f'{url} 账号 {username} 登录时出现错误: {e}')
        return False


async def lqy_cloud_login(page: Page, token):
    # 默认静态 load  动态 networkidle0
    await page.goto(url="http://192.168.50.202:9999/login", waitUntil="networkidle0")

    # await page.waitForSelector("div[class='login']", options={'timeout': 5000})  # 等待特定元素加载最多5秒
    is_logged_in = await page.evaluate('''() => document.querySelector("div[class='login']") != null''')
    if is_logged_in:
        # 获取当前页面的 cookies
        cookies = await page.cookies()
        new_cookie = {
            'name': 'Admin-Token',
            'value': token
        }
        cookies.append(new_cookie)
        await page.setCookie(*cookies)
        print(cookies)
    await asyncio.sleep(1)
    await page.goto(url="http://192.168.50.202:9999/projectManage")


async def main():
    """异步主执行函数"""
    print('==================================================开始执行！')
    browser, page = await chrome_init()
    try:
        if PIG_USERNAME:
            is_logged_in = await login_pig(page, PIG_USERNAME, PIG_PASSWORD, PIG_URL)
            now_utc = datetime.now(timezone.utc).strftime('%Y-%m-%d %H:%M:%S')
            now_beijing = (datetime.now(timezone.utc) + timedelta(hours=8)).strftime('%Y-%m-%d %H:%M:%S')
            if is_logged_in:
                print(f'🐖^(*￣(oo)￣)^ 于北京时间 {now_beijing}（UTC时间 {now_utc}）执行成功！')

        # 获取通过接口登录后的token
        token = utils.verification_code_login.main()
        await lqy_cloud_login(page, token)
        await asyncio.sleep(30)
    finally:
        # 确保关闭浏览器
        await browser.close()
        # time.sleep(1)


if __name__ == '__main__':
    asyncio.run(main())
