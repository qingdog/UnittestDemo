import allure
import pytest
from playwright.sync_api import sync_playwright, Page, Browser

import pytest_project.allure_project.run_allure_with_history

# 定义全局变量以便在多个测试中复用
browser: Browser
page: Page


@pytest.fixture(scope="module", autouse=True)
def browser_setup_and_teardown():
    """
    测试会话的前置和后置步骤：
    - 启动 Playwright 和浏览器
    - 创建一个页面
    """
    pytest_project.allure_project.run_allure_with_history.generate_environment_properties()
    global browser, page
    playwright = sync_playwright().start()
    browser = playwright.chromium.launch(headless=False)
    page = browser.new_page()
    yield  # 测试运行期间，提供全局页面对象供测试使用
    # 测试会话结束后关闭浏览器和 Playwright
    browser.close()
    playwright.stop()


@allure.step("打开页面")
def open_page(url):
    page.goto(url)


def test_example():
    """这是一个示例测试，用于展示 Allure 报告功能"""
    open_page("https://example.com")
    assert "Example Domain" in page.title()


@allure.title("一个错误的示例")
@allure.description("验证 Example 网站标题是否正确，失败时附加更多上下文")
@allure.tag("功能测试", "异常处理")
@allure.severity(allure.severity_level.CRITICAL)
def test_error_example():
    """测试失败时附加上下文"""
    open_page("https://example.com")
    try:
        assert "Example Domain" in page.title()
    except AssertionError as e:
        # 捕获页面截图
        allure.attach(page.screenshot(), name="失败时的页面截图", attachment_type=allure.attachment_type.PNG)
        # 捕获页面内容
        allure.attach(page.content(), name="页面内容", attachment_type=allure.attachment_type.HTML)
        raise e
