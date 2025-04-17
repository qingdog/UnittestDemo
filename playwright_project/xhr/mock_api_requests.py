import re

from playwright._impl._errors import TargetClosedError
from playwright.sync_api import sync_playwright, Page, Route, expect
from playwright_project.find_chrome_util import find_chrome_util
from utils.login_ruoyi_verification_code import login_verification_code


def test_mock_the_fruit_api(page: Page):
    def handle(route: Route):
        # res = requests.session().request(route.request.method, route.request.url, json=route.request.post_data_json, headers=route.request.headers, timeout=10)
        res = route.fetch()
        result: list = res.json()
        route.fulfill(status=200, headers=res.headers, json=[*result, {"name": "apple666", "id": 66}], response=res, )

    # Intercept the route to the fruit API */**/api/v1/fruits
    page.route(re.compile(r".+/fruits"), handle)
    # Go to the page
    page.goto("https://demo.playwright.dev/api-mocking")
    # Assert that the Strawberry fruit is visible
    # expect(page.get_by_text("apple666")).to_be_visible()


def record_har():
    with sync_playwright() as p:
        browser = p.chromium.launch(headless=False, executable_path=find_chrome_util())
        context = browser.new_context()
        page = context.new_page()
        # url = "https://demo.playwright.dev/api-mocking"
        # url = "https://playwright.dev/python/docs/mock#recording-a-har-file"
        url = "http://192.168.50.202:9999/projectManage"
        context.add_cookies([{'name': 'Admin-Token', 'value': login_verification_code(), 'domain': '192.168.50.202', 'path': '/'}])

        test_mock_the_fruit_api(page)

        try:
            page.wait_for_timeout(60 * 1000)
        except TargetClosedError as e:
            print(e)
        finally:
            context.close()


if __name__ == '__main__':
    record_har()
