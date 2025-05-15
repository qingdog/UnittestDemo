import time
import traceback

from DrissionPage.common import from_playwright
from playwright.sync_api import sync_playwright, Page, BrowserContext, expect, Route

from utils.login_ruoyi_verification_code import login_verification_code
from find_chrome_util import find_chrome_util


def chromium_page_from_playwright(playwright_page: Page):
    """从Page对象创建Chromium对象"""
    chromium = from_playwright(playwright_page)
    chromium.latest_tab.get("https://www.drissionpage.cn")


# https://playwright.dev/python/docs/intro#system-requirements
# uname -m # Debian 11, Debian 12, Ubuntu 20.04 or Ubuntu 22.04, Ubuntu 24.04, on x86-64 and arm64 architecture.
def lqy_cloud_login(browser_context: BrowserContext, token: str):
    # page.evaluate('''(token) => {document.cookie=`Admin-Token=${token};`;}''', token)
    new_cookie = [{'name': 'Admin-Token', 'value': token, 'domain': '192.168.50.202', 'path': '/'}]
    browser_context.add_cookies(new_cookie)
    print(browser_context.cookies())
    # page.goto('http://192.168.50.202:9999')
    # page.evaluate('''() =>{ console.log(document.cookie);}''')


def test_mock_the_fruit_api(page: Page):
    def handle(route: Route):
        json = [{"name": "Strawberry1", "id": 21}]
        # fulfill the route with the mock data
        route.fulfill(json=json)

    # Intercept the route to the fruit API
    page.route("*/**/api/v1/fruits", handle)

    # Go to the page
    page.goto("https://demo.playwright.dev/api-mocking")

    # Assert that the Strawberry fruit is visible
    expect(page.get_by_text("Strawberry1")).to_be_visible()


def test_gets_the_json_from_api_and_adds_a_new_fruit(page: Page):
    def handle(route: Route):
        response = route.fetch()
        json = response.json()
        json.append({"name": "Loquat1", "id": 100})
        # Fulfill using the original response, while patching the response body
        # with the given JSON object.
        route.fulfill(response=response, json=json)

    page.route("https://demo.playwright.dev/api-mocking/api/v1/fruits", handle)
    # Go to the page
    page.goto("https://demo.playwright.dev/api-mocking")

    # Assert that the new fruit is visible
    expect(page.get_by_text("Loquat1", exact=True)).to_be_visible()


def test_records_or_updates_the_har_file(page: Page):
    # Get the response from the HAR file
    page.route_from_har("xhr/hars/fruit1.har", url="*/**/api/v1/fruits", update=True)
    # Go to the page
    page.goto("https://demo.playwright.dev/api-mocking")
    # Assert that the fruit is visible
    expect(page.get_by_text("Strawberry")).to_be_visible()


def test_gets_the_json_from_har_and_checks_the_new_fruit_has_been_added(page: Page):
    # Replay API requests from HAR.
    # Either use a matching response from the HAR,
    # or abort the request if nothing matches.
    page.route_from_har("xhr/hars/policy.har", url="*/**/test-api/policylibrary/**/*", update=True)

    # Go to the page
    page.goto("http://192.168.50.202:9999/projectManage")


page: Page
persistent_context: BrowserContext


def main():
    global persistent_context
    global page
    chrome_executable_path = find_chrome_util()
    print(f"\033[34m{chrome_executable_path} #start...\033[0m")
    # with sync_playwright() as playwright_instance:
    playwright = sync_playwright().start()
    # 通过cdp连接到已经启动的 Chrome 浏览器
    # browser = playwright_instance.chromium.connect_over_cdp(f"http://127.0.0.1:{start_remote_chrome_port(chrome_path=chrome_executable_path)}")
    # 启动持久化Chrome
    # C:\Users\Administrator\AppData\Local\ms-playwright\chromium-1155\chrome-win\playwright_user_data
    persistent_context = playwright.chromium.launch_persistent_context(executable_path=chrome_executable_path, headless=False, user_data_dir="temp")
    # persistent_context = playwright.chromium.launch(headless=False, executable_path=chrome_executable_path)
    page = persistent_context.new_page()


    token = login_verification_code()
    lqy_cloud_login(persistent_context, token)

    page.goto(url="http://192.168.50.202:9999/projectManage", wait_until="load")
    page.locator("xpath=//div[@class='option-btn-wrap']/div[text()='编辑']").first.click()
    print(page.title())  # 打印页面标题

    # test_gets_the_json_from_api_and_adds_a_new_fruit(page)
    # test_records_or_updates_the_har_file(page)
    test_gets_the_json_from_har_and_checks_the_new_fruit_has_been_added(page)


if __name__ == '__main__':
    try:
        main()
        time.sleep(10)  # 延时，便于观察结果
        globals().get("persistent_context").close()
    except Exception as e:
        print(f"\033[35m{traceback.format_exc()}\033[0m")
        # main()  # 异常就重试一次
    finally:
        pass
