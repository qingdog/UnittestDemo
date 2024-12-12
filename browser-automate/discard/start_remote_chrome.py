import os
import time

import psutil
from playwright.sync_api import sync_playwright


def check_port(port):
    """检查端口是否被占用"""
    for conn in psutil.net_connections(kind='inet'):
        if conn.laddr.port == port:
            return True
    return False


def start_remote_chrome_port(chrome_path=r"C:/Program Files/Google/Chrome/Application/chrome.exe", port=9527):
    """初始化浏览器连接"""
    if not check_port(port):
        print(f"端口 {port} 没有被占用，启动 Chrome 浏览器...")
        os.system(
            rf'start "" "{chrome_path}" --remote-debugging-port={port} '  # 避免start遇到空格就结束
            r'--user-data-dir="D:\\selenium"&')
    else:
        print(f"端口 {port} 已经被占用，Chrome 浏览器已启动。")

    return port


if __name__ == '__main__':
    chrome_port = start_remote_chrome_port()
    with sync_playwright() as p:
        browser = p.chromium.connect_over_cdp(f"http://127.0.0.1:{chrome_port}")
        # browser = p.chromium.launch(executable_path=chrome_executable_path, headless=False)
        context = browser.contexts[0]
        page = context.pages[0]

        # 打印 navigator.webdriver 的值
        print("navigator.webdriver: " + page.evaluate('navigator.webdriver'))

        page.goto("http://localhost:9527/json/version")
        time.sleep(3)
        page.goto("https://bot.sannysoft.com/")
        # 执行操作，例如获取页面标题
        print(page.title())
        # 延时，便于观察结果
        time.sleep(60)
        browser.close()
