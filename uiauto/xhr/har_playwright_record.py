import re
import time

from playwright.sync_api import sync_playwright, Page, expect
from uiauto.find_chrome_util import find_chrome_util


def test_records_or_updates_the_har_file(page: Page, url):
    # Get the response from the HAR file
    re_pattern = r"^http(s)?://[\d\.a-z:]+/"
    result = re.search(rf"{re_pattern}", url)
    prefix = result.group(0) if result else re_pattern
    page.route_from_har(f"./hars/{time.strftime('%Y%m%d')}.har", url=re.compile(rf"{prefix}[a-z\d\-/]*[a-z\d\-]+$"), update=True)
    # page.route_from_har(f"./hars/{time.strftime('%Y%m%d')}.har", url=re.compile(r"^http(s)?://[\d\.a-z:]+/[a-z\d\-/]*[a-z\d\-]+$"), update=True)
    page.goto(url)
    # page.goto("https://playwright.dev/python/docs/codegen-intro")


def record_har():
    with sync_playwright() as p:
        browser = p.chromium.launch(headless=False, executable_path=find_chrome_util())
        context = browser.new_context()
        page = context.new_page()
        # url = "https://demo.playwright.dev/api-mocking"
        url = "https://playwright.dev/python/docs/mock#recording-a-har-file"
        test_records_or_updates_the_har_file(page, url=url)
        time.sleep(10)
        context.close()


if __name__ == '__main__':
    record_har()
