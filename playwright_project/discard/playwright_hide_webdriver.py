import requests
from playwright.sync_api import sync_playwright
import time


def main():
    with sync_playwright() as p:
        '''
        防止被浏览器检测的处理方法
        '''
        browser = p.chromium.launch(executable_path="C:/Program Files/Google/Chrome/Application/chrome.exe",
                                    headless=False)
        page = browser.new_page()
        url = 'https://raw.githubusercontent.com/requireCool/stealth.min.js/main/stealth.min.js'
        url = 'https://gitee.com/zenyifan/stealth.min.js/raw/main/stealth.min.js'
        response = requests.get(url)
        js = response.text
        # with open('stealth.min.js', 'r') as f:
        #     js = f.read()
        page.add_init_script(js)

        page.goto('https://bot.sannysoft.com/')

        time.sleep(60)
        browser.close()


def browser_headless():
    with sync_playwright() as p:
        '''
        无头模式，添加User-Agent并设置视口大小
        '''
        user_agent = "--user-agent=Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/130.0.0.0 Safari/537.36"
        # browser = p.chromium.launch(headless=True, args=["--headless=new"], executable_path=find_chrome_util())
        browser = p.chromium.launch(headless=True, args=['--disable-blink-features=AutomationControlled', user_agent],
                                    executable_path="C:/Program Files/Google/Chrome/Application/chrome.exe")
        page = browser.new_page()
        url = 'https://gitee.com/zenyifan/stealth.min.js/raw/main/stealth.min.js'
        response = requests.get(url)
        js = response.text
        page.add_init_script(js)
        # 设置网页大小也可以防止无头浏览器被检测
        page.set_viewport_size({'width': 1600, 'height': 900})

        page.goto('https://bot.sannysoft.com/')
        # 进行截图
        page.screenshot(path='headless_test.png', full_page=True)

        time.sleep(3)
        browser.close()


if __name__ == '__main__':
    # main()
    browser_headless()
