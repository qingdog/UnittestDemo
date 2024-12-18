import os
import platform
import time
import traceback

from DrissionPage import ChromiumPage, ChromiumOptions
from DrissionPage._base.chromium import Chromium
from DrissionPage._elements.chromium_element import ChromiumElement
from DrissionPage._pages.mix_tab import MixTab
from dotenv import load_dotenv
from lxml import etree


# pip install DrissionPage #https://drissionpage.cn
def god_index(tab: MixTab, token: str):
    """首页点击"""
    tab.get("https://gptgod.online/#/session/42zim85h27okj37t5icb04o2k")
    '''ele1 = tab.eles('xpath:/html/body')  # 微信截图的position 减标签及url栏高度得到 按钮相对body的高度
    if len(ele1) > 0:
        print(ele1[0])
        ele1[0].click.at(312, 927.5)
        ele1[0].click.at(312, 859)'''
    time.sleep(5)
    print("sleep5...")
    tab.wait.load_start()
    print("wait.load_start...")
    click_cloudflare_turnstile(tab, None)


def god_checkin(tab: MixTab, token: str):
    # tab.get("https://gptgod.online/#/token?tab=rule")
    cookies = f'EGG_SESS={token}; path=/; domain=gptgod.online;'
    tab.set.cookies(cookies)
    # tab.get("https://www.baidu.com")
    time.sleep(0.5)
    tab.get("https://gptgod.online/#/token?tab=rule")
    print(tab.cookies())
    print(tab.eles('xpath=//*[@id="root"]/div/div[2]/aside/div/div[3]/div/div[2]/div/div[7]/button/div')[0].text)
    # tab.scroll.down(20)

    css_buttons = tab.eles("css:button.ant-btn.css-1jr6e2p.ant-btn-default.ant-btn-color-default.ant-btn-variant-outlined")
    tab.wait(30, 30)
    # buttons = tab.eles("xpath=//button[span[text()='签到 领取2000积分']]")
    buttons = css_buttons
    if len(buttons) == 0:
        if len(css_buttons) > 0: print(css_buttons[0].text)
        print("没有找到按钮")
        return
    button_el = buttons[0]
    # 滚动页面使自己可见
    # button_el.scroll.to_see()
    # 按类型查找 同类型样式的多个按钮
    print(button_el.text)  # 签到
    try:
        # print(f"{button_el.rect.click_point} click...")
        # print(f"{button_el.rect.viewport_click_point} viewport_click_point...")
        pass
    except Exception as e:
        print(e)
    finally:
        # print(f"{button_el.states.has_rect} click...")
        # button_el.click(by_js=True)
        button_el.click()
        start_time = time.time()
        tab.wait.load_start()  # 等待页面进入加载状态
        print(time.time() - start_time)
        tab.wait(30, 30)
        click_cloudflare_turnstile(tab, button_el)


def click_cloudflare_turnstile(tab: MixTab, button: ChromiumElement = None):
    """点击cf真人认证"""
    # tab.wait.ele_displayed()
    elements = tab.eles('css:#cf-turnstile')
    if len(elements) == 0:
        print("没有找到#cf-turnstile")
        # return
        tab.wait(40, 40)
        elements = tab.eles('css:#cf-turnstile')
        if len(elements) == 0: return
    cf_turnstile_ele = elements[0]
    '''
    # width, height = cf_turnstile_ele.rect.size
    # print(f"{width, height}: {cf_turnstile_ele}")'''

    # cf_turnstile_ele.click.right()
    # 点击元素上中部，x相对左上角向右偏移50，y保持在元素中点
    # cf_turnstile_ele.click.at(offset_x=28, offset_y=32, button="right", count=1)
    time.sleep(2)
    cf_turnstile_ele.click.at(offset_x=28, offset_y=32)  # 正中复选框
    print("86 tab.wait.load_start...")
    tab.wait.load_start()  # 等待页面加载

    if button:
        print(button.text)
        if button.text == "今天已签到": return
    tab.wait(20, 20)
    print("已经点击wait20s...")
    tab.wait.load_start()  # 等待页面加载
    try:
        if cf_turnstile_ele.states.has_rect:
            top_left, top_right, bottom_right, bottom_left = cf_turnstile_ele.states.has_rect
            print(top_left, top_right, bottom_right, bottom_left)
            width, height = tab.eles('css:#cf-turnstile')[0].rect.size
            print(f"{width, height}: {tab.eles('css:#cf-turnstile')[0]}")
            # tab.eles('css:#cf-turnstile')[0].click.at(offset_x=28, offset_y=32)
            # tab.get_screenshot(path='tmp', name='wait_click_bak.jpg', full_page=True)
            tab.wait(1, 2)

            # 获取元素大小
            width = tab.run_js("""
                console.log(document.querySelector('#cf-turnstile'))
                return document.querySelector('#cf-turnstile').getBoundingClientRect().width;
                """)
            print(width, height)
            button.click()
            tab.scroll.down(61)
            # tab.get_screenshot(path='tmp', name='wait_click1_hide.jpg', full_page=True)
            tab.wait(60)
            tab.scroll.up(82)
            button.click()
            # tab.get_screenshot(path='tmp', name='wait_click2_display.jpg', full_page=True)
            tab.wait(3)
            tab.scroll.down(30)
            tab.wait(60)
            # tab.get_screenshot(path='tmp', name='wait_click2_wait.jpg', full_page=True)
            cf_turnstile_ele.click.at(width / 4, 30)  # 不点击
            time.sleep(20)
    except Exception as e:
        print(f"\033[35m{traceback.format_exc()}\033[0m")
        w = 238
        height = 782
        # 40,698
    finally:
        ele1 = tab.eles('xpath:/html/body')  # 微信截图的position 减标签及url栏高度得到 按钮相对body的高度
        if len(ele1) > 0:
            time.sleep(30)
            ele1[0].click.at(238, 720)
            print(button.text)
            time.sleep(30)
            ele1[0].click.at(40, 720)
        print(button.text)


global chromium


def main_bak():
    # 配置 Chromium 选项
    chromium_options = ChromiumOptions().set_load_mode("normal")
    user_agent = "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/130.0.0.0 Safari/537.36"
    chromium_options.headless(on_off=True).set_user_agent(user_agent).set_argument('--window-size', '1800, 900')
    chromium_options.set_argument("--no-sandbox")
    chromium_options.set_argument("--disable-setuid-sandbox")
    # chromium_options.set_argument("--headless=new")  # 无界面系统添加
    chromium_options.set_paths(local_port=9222)
    # 兼容无头模式中的参数 --headless=new
    if not chromium_options.is_headless:
        chromium_options.remove_argument("--headless=new")
    global chromium
    try:
        chromium = Chromium(chromium_options)
        tab = chromium.latest_tab
        token = os.getenv("EGG_SESS")

        def set_cookies(_tab, _token):
            cookies = f'EGG_SESS={_token}; path=/; domain=gptgod.online;'
            _tab.set.cookies(cookies)
            print(_tab.cookies())

        def click_turnstile(tab):
            """处理 Turnstile 验证和点击动作"""
            elements = tab.eles('css:#cf-turnstile')
            if elements:
                elements[0].click.at(28, 32)  # 点击验证码复选框
                print("Clicked on Turnstile.")
            else:
                print("No Turnstile element found.")

        def wait_for_load(tab):
            """等待页面加载完成"""
            print("Waiting for page to load...")
            tab.wait.load_start()  # 等待页面加载开始
            # tab.get_screenshot(path='tmp', name='wait_load_start.jpg')
            tab.wait.load_start()  # 等待页面加载完成
            # tab.get_screenshot(path='tmp', name='wait_done.jpg')

        # 设置 Cookies
        set_cookies(tab, token)

        url = "https://gptgod.online/#/token?tab=rule"
        tab.get(url)
        time.sleep(1)
        print(tab.cookies())

        print(tab.ele('xpath=//*[@id="root"]/div/div[2]/aside/div/div[3]/div/div[2]/div/div[7]/button/div').text)
        tab.scroll.down(100)

        # 查找按钮并点击
        buttons = tab.eles("css:button.ant-btn.css-1jr6e2p.ant-btn-default.ant-btn-color-default.ant-btn-variant-outlined")
        if buttons:
            print(buttons[0].text)
            buttons[0].click()
            print("Button clicked.")
            wait_for_load(tab)

            click_turnstile(tab)  # 处理验证码

        # 打印 cf-turnstile-response 的值
        cf_turnstile_response = etree.HTML(tab.html).xpath('//*[@name="cf-turnstile-response"]/@value')
        print(f"cf_turnstile_response: {cf_turnstile_response}")
    except Exception as e:
        print(f"\033[34m{traceback.format_exc()}\033[0m")
    finally:
        if globals().get("chromium"):
            print("quit...")
            chromium.quit()


def main():
    os_name = platform.system()
    chromium_options = ChromiumOptions()
    if os_name != "Windows":
        user_agent = "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/130.0.0.0 Safari/537.36"
        chromium_options.headless(on_off=True).set_user_agent(user_agent).set_argument('--window-size', '1920, 1080')
        chromium_options.set_argument("--no-sandbox")
        chromium_options.set_argument("--disable-setuid-sandbox")
        # chromium_options.set_argument('--start-maximized')
        chromium_options.set_argument("--headless=new")  # 无界面系统添加
        chromium_options.incognito(on_off=True)  # chrome.exe --incognito
    else:
        user_agent = "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/130.0.0.0 Safari/537.36"
        chromium_options.headless(on_off=True).set_user_agent(user_agent).set_argument('--window-size', '1920, 1080')
        chromium_options.set_argument("--no-sandbox")
        chromium_options.set_argument("--disable-setuid-sandbox")
        chromium_options.set_argument("--headless=new")  # 无界面系统添加
    # 设置加载图片、静音
    chromium_options.no_imgs(False).mute(True)
    # https://drissionpage.cn/versions/4.0.x #linux取消了自动无头模式浏览器，使用 chrome 关键字路径
    chromium_page = ChromiumPage(chromium_options.set_load_mode('normal').set_paths(browser_path=None))
    try:
        tab = Chromium().latest_tab

        load_dotenv()
        token = os.getenv("EGG_SESS")
        time.sleep(1)
        god_checkin(tab, token)
        # god_index(tab, token)

        print(f"cf-turnstile-response: {etree.HTML(tab.html).xpath('//*[@name="cf-turnstile-response"]')}")
    except Exception as e:
        raise e
    finally:
        print("done.")
        time.sleep(60)
        chromium_page.quit()  # 关闭浏览器


if __name__ == '__main__':
    load_dotenv()
    try:
        main_bak()
    except Exception:
        print(f"\033[34m{traceback.format_exc()}\033[0m")
        main()  # 异常就重试一次
