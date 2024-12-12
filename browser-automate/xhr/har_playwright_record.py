import re
import time

from playwright._impl._errors import TargetClosedError
from playwright.sync_api import sync_playwright, Page, expect
from uiauto.find_chrome_util import find_chrome_util
from utils.login_ruoyi_verification_code import login_verification_code


def test_records_or_updates_the_har_file(page: Page, url):
    # Get the response from the HAR file
    re_pattern = r"^http(s)?://[\d\.a-z:]+/"
    result = re.search(rf"{re_pattern}", url)
    prefix = result.group(0) if result else re_pattern
    # 只根据域名进行录制接口请求
    page.route_from_har(f"./hars/{time.strftime('%Y%m%d')}.har", url=re.compile(rf"{prefix}[a-z\d\-/]*[a-z\d\-]+$"), update=True)
    # 录制所有ip域名请求，不录制js、css、png等请求
    # page.route_from_har(f"./hars/{time.strftime('%Y%m%d')}.har", url=re.compile(r"^http(s)?://[\d\.a-z:]+/[a-z\d\-/]*[a-z\d\-]+$"), update=True)
    page.goto(url)
    # page.goto("https://playwright.dev/python/docs/codegen-intro")


def record_har():
    with sync_playwright() as p:
        browser = p.chromium.launch(headless=False, executable_path=find_chrome_util())
        context = browser.new_context()
        page = context.new_page()
        # url = "https://demo.playwright.dev/api-mocking"
        # url = "https://playwright.dev/python/docs/mock#recording-a-har-file"
        url = "http://192.168.50.202:9999/projectManage"
        context.add_cookies([{'name': 'Admin-Token', 'value': login_verification_code(), 'domain': '192.168.50.202', 'path': '/'}])

        test_records_or_updates_the_har_file(page, url=url)

        try:
            page.wait_for_timeout(60 * 1000)
        except TargetClosedError as e:
            print(e)
        finally:
            context.close()


if __name__ == '__main__':
    record_har()
