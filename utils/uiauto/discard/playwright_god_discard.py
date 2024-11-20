import random
import time
import traceback

from playwright.sync_api import sync_playwright, Page, BrowserContext

from utils.uiauto.discard.playwright_turnstile_discard import cloudflare_turnstile
from utils.uiauto.find_chrome_util import find_chrome_util

# https://playwright.dev/python/docs/intro#system-requirements
# uname -m # Debian 11, Debian 12, Ubuntu 20.04 or Ubuntu 22.04, Ubuntu 24.04, on x86-64 and arm64 architecture.
def god_login(page: Page, browser_context: BrowserContext, token):
    new_cookie = [{
        'name': 'EGG_SESS',
        'value': token,
        'domain': 'gptgod.online',
        'path': '/'
    }]
    browser_context.add_cookies(new_cookie)

    # 也可以进行等待按钮点击
    # await page.waitForSelector("div[class='login']", options={'timeout': 5000})

    # page.goto(url="https://gptgod.online/#/token?tab=rule", wait_until="networkidle")
    page.goto(url="https://gptgod.online/#/session/4r5me8ro1tsyctyimx0lpmd3r", wait_until="networkidle")
    """page.goto(url="https://gptgod.online/#/session/4r5me8ro1tsyctyimx0lpmd3r", wait_until="networkidle")
    time.sleep(random.uniform(0.5, 1))
    check_button = page.wait_for_selector("#rc-tabs-0-panel-rule> div> button")
    
    check_button.wait_for_element_state(state="stable")
    print(check_button)
    # 滚动到元素
    time.sleep(random.uniform(0.2, 0.5))
    check_button.scroll_into_view_if_needed()
    time.sleep(random.uniform(0.2, 0.5))
    # 或者你也可以手动使用 JavaScript 来进行滚动操作

    check_button.click()"""
    page.wait_for_timeout(random.uniform(3, 3) * 1000)  # 等待js执行完
    page.screenshot(path='cf-networkidle1.png', full_page=True)
    page.wait_for_load_state('networkidle')  # 等待网络空闲
    page.screenshot(path='cf-networkidle2.png', full_page=True)
    print("假设网络已经空闲（待定）...")
    page.wait_for_timeout(random.uniform(1, 1) * 1000)  # 网络空闲之后模拟真人等待
    # TODO 假设网络已经空闲（待定） 11.09
    cloudflare_turnstile(page)


def main():
    chrome_executable_path, chrome_startup_args = find_chrome_util()
    print(f"{chrome_executable_path} #start...")
    with sync_playwright() as p:
        # 通过cdp连接到已经启动的 Chrome 浏览器
        # port = remote_chrome.start_remote_chrome_port(chrome_path=chrome_executable_path)
        # browser = p.chromium.connect_over_cdp(f"http://127.0.0.1:{port}")
        # 不连接，直接启动浏览器
        browser = p.chromium.launch(executable_path=chrome_executable_path, headless=False)
        context = browser.contexts[0]
        page = context.pages[0]

        # lqy_cloud_login(page, context, verification_code_login())
        token = "MGvQ7xB3RBm6dW1ejBpt4NFNsmtVdSOUYx10mzsQSZyco7RUh41IkIVYomBRF1yR"
        token = ""
        god_login(page, context, token)

        # 延时，便于观察结果
        page.wait_for_timeout(random.uniform(60, 60) * 1000)
        browser.close()


if __name__ == '__main__':
    try:
        main()
    except Exception as e:
        print(f"\033[34m{traceback.format_exc()}\033[0m")
        time.sleep(3)
        main()  # 异常就重试一次
    finally:
        pass
