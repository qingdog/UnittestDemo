import random
import time
from playwright.sync_api import sync_playwright, Page, BrowserContext, ElementHandle

from utils.uiauto.find_chrome_util import find_chrome_util


def cloudflare_turnstile(page: Page, selector="#cf-turnstile"):
    for _ in range(30):
        x, y = get_x_y(page, selector=selector)
        if x:
            print(x ,y ,end="")
            children_before_el = get_children_at_position(page, x, y)
            if children_before_el:
                # 等待node引用到一个具体的 HTML 元素如input，这里用于打印输出
                children_before_el.wait_for_element_state(state="stable", timeout=5000)
                print(f"before: {children_before_el}")
                children_before_value = children_before_el.input_value()

                range_len = 5
                sleep_time = 20
                for _ in range(range_len):
                    # 执行点击操作
                    page.mouse.click(x, y)
                    result = get_children_at_position(page, x, y)
                    if result is None: break  # 外循环已经获取到get_children_at_position后，内循环获取变成为None则确认为执行完毕
                    val = result.input_value()
                    print(f"{val}", end="")
                    if val != children_before_value:
                        print(f"after: {result}")
                        break
                    if _ != range_len - 1:
                        sleep_time += random.uniform(2, 10) # 使用20s进行递增时间睡眠
                        print(f"{sleep_time}. ", end="")
                        time.sleep(sleep_time)
                else:
                    print("已等待120s click失败.")
                break
        print(f".", end="")
        time.sleep(1)
    else:
        print("已等待30s findElement失败.")

    print(f"{page.title()} -> cloudflare_turnstile done.")


def get_x_y(page: Page, selector='#cf-turnstile'):
    turnstile_el = page.wait_for_selector(selector, timeout=5000)  # 设置等待超时，避免长时间阻塞
    if not turnstile_el:
        print("未能找到元素")
        return None, None

    bounding_box = turnstile_el.bounding_box()
    if not bounding_box:
        print("未能获取元素边界框")
        return None, None

    # 计算点击坐标
    x = bounding_box['x'] + bounding_box['width'] / 4  # 点击左侧
    # 通过cf-turnstile定位不准问题
    # print(f"x: {x}")
    # x = 312  # 点击左侧
    y = bounding_box['y'] + bounding_box['height'] / 2  # 点击中央
    return x, y


def get_children_at_position(page, x, y):
    try:
        # 使用 evaluate 执行 JavaScript，获取点击位置的元素标签
        evaluate_handle: ElementHandle = page.evaluate_handle('''(coord) => {
                const element = document.elementFromPoint(coord.x, coord.y);
                if (element) {
                    console.log("元素在：", coord.x, coord.y, element);
                    if (element.children.length > 0) {
                        ins = element.querySelectorAll("input")
                        return ins.length > 0 ? ins[0] : null;
                    }
                }
                return null;
            }''', {'x': x, 'y': y})  # 将 x 和 y 作为字典传递
        return evaluate_handle.as_element()
    except Exception as e:
        print(f"获取元素时发生错误: {e}")
    return None


def main():
    """废弃"""
    with sync_playwright() as playwright:
        chrome_executable_path, chrome_startup_args = find_chrome_util()
        print(f"{chrome_executable_path} #start...")
        browser = playwright.chromium.launch(executable_path=chrome_executable_path, headless=False)
        context = browser.new_context()
        page = context.new_page()

        # 默认静态 load  动态 networkidle
        page.goto("https://2captcha.com/demo/cloudflare-turnstile/", wait_until="load")
        print("load...")
        page.wait_for_load_state(state="networkidle")
        print("networkidle.")
        cloudflare_turnstile(page)

        page.goto("https://nopecha.com/captcha/turnstile", wait_until="networkidle")
        cloudflare_turnstile(page, selector="#example-container5")

        time.sleep(60)
        browser.close()


if __name__ == '__main__':
    main()
