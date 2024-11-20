import asyncio
import logging
import platform
import subprocess
import os
from datetime import datetime, timedelta, timezone

from pyppeteer import launch
from dotenv import load_dotenv

load_dotenv()
# 环境变量
PIG_URL = os.getenv('PIG_URL')
PIG_USERNAME = os.getenv('PIG_USERNAME')
PIG_PASSWORD = os.getenv('PIG_PASSWORD')

OS_NAME = platform.system()

# Pyppeteer 也可以用来控制 Chrome 浏览器，但与它捆绑的 Chromium 版本配合最佳。无法保证它与其他版本兼容。请谨慎使用 executablePath 选项
debug_chrome_path = "C:\Program Files\Google\Chrome\Application\chrome.exe"
chrome_executable_path = debug_chrome_path if OS_NAME == "Windows" else subprocess.check_output(['which', 'google-chrome']).decode().strip()
# is_headless = OS_NAME != "Windows"  # 非windows则以无头模式启动
is_headless = True
chrome_startup_args = ['--no-sandbox', '--disable-setuid-sandbox']


async def chrome_init():
    """初始化 Chrome 浏览器并返回页面实例"""
    print(f"start '{chrome_executable_path}' # starting...")
    browser = await launch(headless=is_headless, args=chrome_startup_args, executablePath=chrome_executable_path)
    # page = browser.newPage()
    page = (await browser.pages())[0]
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
                """navigation_promise = asyncio.ensure_future(page.waitForNavigation())  # 启动等待导航的任务
                await login_button.click()
                await page.content()
                await navigation_promise"""
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


async def main():
    """异步主执行函数"""
    print('==================================================pig开始执行！')
    browser, page = await chrome_init()
    is_logged_in = await login_pig(page, PIG_USERNAME, PIG_PASSWORD, PIG_URL)

    await browser.close()

    # 将日期格式化为 ISO 字符串
    now_utc = datetime.now(timezone.utc).strftime('%Y-%m-%d %H:%M:%S')
    now_beijing = (datetime.now(timezone.utc) + timedelta(hours=8)).strftime('%Y-%m-%d %H:%M:%S')
    if is_logged_in:
        print(f'🐖^(*￣(oo)￣)^ 于北京时间 {now_beijing}（UTC时间 {now_utc}）登录成功！')


if __name__ == '__main__':
    # 这里不区分OS直接执行
    asyncio.run(main())
