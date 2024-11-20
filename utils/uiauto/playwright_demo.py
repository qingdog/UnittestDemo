import time
import traceback

from DrissionPage.common import from_playwright
from playwright.sync_api import sync_playwright, Page, BrowserContext

from utils.login_ruoyi_verification_code import login_verification_code
from utils.uiauto.find_chrome_util import find_chrome_util


# https://playwright.dev/python/docs/intro#system-requirements
# uname -m # Debian 11, Debian 12, Ubuntu 20.04 or Ubuntu 22.04, Ubuntu 24.04, on x86-64 and arm64 architecture.
def lqy_cloud_login(page: Page, browser_context: BrowserContext, token: str):
    page.goto(url="http://192.168.50.202:9999", wait_until="load")
    new_cookie = [{
        'name': 'Admin-Token',
        'value': token,
        'domain': '192.168.50.202',
        'path': '/'
    }]
    browser_context.add_cookies(new_cookie)

    # page.evaluate('''(token) => {document.cookie=`Admin-Token=${token};`;}''', token)
    print(browser_context.cookies())
    page.evaluate('''() =>{ c = document.cookie; console.log(c);}''')
    # page.locator("button")
    page.goto(url="http://192.168.50.202:9999/projectManage", wait_until="load")
    time.sleep(5)
    page.locator("xpath=//div[@class='option-btn-wrap']/div[text()='编辑']").first.click()

    time.sleep(5)

    print(page.title())  # 打印页面标题


def main():
    chrome_executable_path, chrome_startup_args = find_chrome_util()
    print(f"{chrome_executable_path} #start...")
    with sync_playwright() as p:
        # 通过cdp连接到已经启动的 Chrome 浏览器
        # port = remote_chrome.start_remote_chrome_port(chrome_path=chrome_executable_path)
        # browser = p.chromium.connect_over_cdp(f"http://127.0.0.1:{port}")
        # 不连接，直接启动浏览器
        browser = p.chromium.launch(executable_path=chrome_executable_path, headless=False)
        # context = browser.contexts[0]
        # page = context.pages[0]

        context = browser.new_context()
        page = context.new_page()

        token = login_verification_code()
        lqy_cloud_login(page, context, token)

        # 延时，便于观察结果
        page.wait_for_timeout(30000)
        browser.close()


def chromium_page_from_playwright(playwright_page: Page):
    # 从Page对象创建ChromiumPage对象
    chromium_page = from_playwright(playwright_page)
    # 用ChromiumPage对象操作浏览器
    chromium_page.latest_tab.get("https://www.DrissionPage.cn")


if __name__ == '__main__':
    try:
        main()
    except Exception as e:
        print(f"\033[34m{traceback.format_exc()}\033[0m")
        time.sleep(3)
        # main()  # 异常就重试一次
    finally:
        pass
