import platform
import time
import traceback

from DrissionPage import ChromiumOptions
from DrissionPage._base.chromium import Chromium
from DrissionPage._pages.chromium_tab import ChromiumTab
from dotenv import load_dotenv

from utils.login_ruoyi_verification_code import login_verification_code

tab: ChromiumTab
os_name = platform.system()


def check_message():
    return len(tab.eles("css=.el-message.el-message--success")) > 0


def add_project():
    tab.get("http://192.168.50.202:9999/projectManage", timeout=10)

    tab.eles("xpath=//button[span[text()='新增']]")[0].click()
    tab.eles("xpath=//input[@placeholder='请输入项目名称']")[0].input(f"测试test{time.strftime("%Y-%m-%d_%H:%M")}")
    tab.eles("xpath=//div[span[text()='请选择项目类型']]")[0].click()
    tab.eles("xpath=//li[span[text()='财务、税收优惠']]")[0].click()

    tab.eles("xpath=//label[text()='组织部门']")[0].parent().click()
    tab.eles("xpath=//li[span[text()='钓鱼岛-钓鱼岛发展']]")[0].click()

    tab.eles("xpath=//div[span[text()='请选择项目分类']]")[0].click()
    tab.eles("xpath=//li[span[text()='普惠型']]")[0].click()

    tab.eles("xpath=//button[span[text()='添加']]")[0].click()
    tab.eles("xpath=//div[span[text()='请选择行业']]")[0].click()
    tab.eles("xpath=//div[span[text()='制造业']]")[0].parent().ele("xpath=./div/label").click()
    tab.eles("xpath=//button[span[text()='确 定']]")[0].click()

    tab.get_frame('css=#ueditor_2').ele("xpath=//html/body").input("地区\n行业")

    iframe = tab.get_frame('css=#ueditor_3')
    iframe.ele("xpath=//html/body").input(1)
    tab.eles("xpath=//button[span[text()='提交审核']]")[0].click()

    tab.wait.doc_loaded()
    if check_message():
        text = "用例1：新增项目成功！"
        print(f"\033[32m{text}\033[0m")


def select_project():
    tab.get("http://192.168.50.202:9999/projectManage")
    tab.eles("xpath=//input[@placeholder='输入项目名称进行查询']")[0].input(f"测试test{time.strftime("%Y-%m-%d")}", clear=True)
    tab.eles("xpath=//button[span[text()='搜索']]")[0].click()

    if tab.eles("css=tbody>tr>td")[1].text.find("测试test") != -1:
        text = "用例2：查询项目成功！"
        print(f"\033[32m{text}\033[0m")


def del_project():
    tab.eles("xpath=//div[@class='el-dropdown']/div[' 更多 ']")[0].hover()
    tab.eles("xpath=//li[text()='删除']")[0].click()
    tab.wait.doc_loaded()
    tab.eles("xpath=//button/span[text()='确定']")[0].click()


def audit_project():
    print(tab.eles("xpath=//div[@class='option-btn-wrap']/div[text()='审核']"))
    tab.eles("xpath=//div[@class='option-btn-wrap']/div[text()='审核']")[0].click(by_js=True)
    tab.eles("xpath=//label/span[text()='通过']")[0].click()
    tab.eles("xpath=//button[span[text()='确 定']]")[0].click()
    if check_message():
        text = "用例3：审核项目成功！"
        print(f"\033[32m{text}\033[0m")


def edit_project():
    tab.get("http://192.168.50.202:9999/projectManage")
    tab.wait.doc_loaded()
    tab.eles("xpath=//div[@class='option-btn-wrap']/div[text()='编辑']")[0].click()

    # tab.eles("xpath=//div[@class='option-btn-wrap']/div[text()='编辑']")[0].click(by_js=True)
    # tab.eles("css=div.option-btn-wrap>div.link-text")[1].click()
    # tab.eles("xpath=//div[@class='option-btn-wrap']/div[text()='编辑']")[0].click.at(offset_x=10)

    # tab.wait.doc_loaded()
    tab.eles("xpath=//button[span[text()='保存']]")[0].click()
    if check_message():
        text = "用例4：编辑项目成功！"
        print(f"\033[32m{text}\033[0m")


def project_manage_marking():
    tab.wait.doc_loaded()
    tab.eles("xpath=//div[@class='el-dropdown']/div[' 更多 ']")[0].hover()
    tab.ele("xpath=//li[text()='打标']").click()
    tab.wait.doc_loaded()
    tab.eles("xpath=//button/span[text()=' 新增组 ']")[0].click()
    left_container_p = tab.ele('css=div.annotator-container>div>p')
    left_container_p_len = len(left_container_p.text)
    if left_container_p_len > 0:
        if left_container_p_len > 29: left_container_p_len = 29  # 24寸显示器一行最多29个文字
        width = (left_container_p_len - 0) * 16 - 16 / 1.2  # 16px
        left_container_p.click.at(offset_x=width, count=2, button="left")  # 双击最后一个字
        left_container_p.click.at(offset_x=width, count=1, button="right")

        tab.ele("xpath=//div[@class='rightMenu-item']/span[text()='行业要求']").click()
        # 选择行业
        tab.ele("xpath=//button/span[text()='关联']").click()
        tab.eles("xpath=//div[span[text()='请选择行业']]")[0].click()
        tab.eles("xpath=//div[span[text()='制造业']]")[0].parent().ele("xpath=./div/label").click()
        tab.eles("xpath=//button[span[text()='确 定']]")[0].click()
        tab.eles("xpath=//tr/td[last()]/div/div/div/i")[0].click()

        if check_message():
            text = "用例5：项目打标制造业成功！"
            print(f"\033[32m{text}\033[0m")


def main():
    global tab
    chromium_options = (ChromiumOptions().set_load_mode('normal').set_paths(browser_path=None, user_data_path=None, cache_path=None)
                        .no_imgs(False).mute(True).headless(on_off=False))  # 设置不加载图片、静音
    if os_name != "Windows":
        # https://drissionpage.cn/versions/4.0.x #linux取消了自动无头模式浏览器，使用 chrome 关键字路径
        user_agent = "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/130.0.0.0 Safari/537.36"
        chromium_options.headless(on_off=True).set_user_agent(user_agent).set_argument('--window-size', '1920, 1080')
        '''chromium_options.set_argument("--no-sandbox")
        chromium_options.set_argument("--disable-setuid-sandbox")
        chromium_options.set_argument('--start-maximized')'''
        # chrome.exe --incognito
        # chromium_options.incognito().set_argument("--headless=new")  # 无界面系统添加
    # 兼容无头模式中的参数 --headless=new
    if not chromium_options.is_headless:
        chromium_options.remove_argument("--headless=new")
    chromium_page = Chromium(chromium_options)
    chromium_page.set.timeouts(10, 10, 10)
    tab = chromium_page.latest_tab

    load_dotenv()
    token = login_verification_code()

    def save_cookie(_token: str):
        # tab.run_js("((token) => { document.cookie=`Admin-Token=${token};`; })('%s')" % token)
        tab.set.cookies(f'Admin-Token={_token}; path=/; domain=192.168.50.202;')
        tab.run_js('''((s) =>{ console.log(s);})("设置cookie登录 "+document.cookie)''')

    save_cookie(token)

    '''add_project()
    select_project()
    audit_project()
    edit_project()'''

    select_project()
    project_manage_marking()

    # del_project()

    '''tab.get("http://192.168.50.202:9999/enterpriseInforManage")
    tab.ele('xpath=//button/span[text()="详情"]').click()
    tab.get("http://192.168.50.202:9999/projectManage")
    # tab.ele('xpath=//div/div[text()="编辑"]').click()
    tab.ele("xpath=//div[@class='option-btn-wrap']/div[text()='编辑']").click()'''


if __name__ == '__main__':
    try:
        main()
    except KeyboardInterrupt as e:
        print(f"\033[34m{traceback.format_exc()}\033[0m") # 蓝色中断异常
    except Exception as e:
        print(f"\033[35m{traceback.format_exc()}\033[0m") # 紫色全局异常
        # main()  # 异常就重试一次
    finally:
        print("finally.")
        time.sleep(30) # 睡眠延时30s，便于观察结果
        # pycharm强行关闭运行进程会触发回收资源关闭Windows浏览器
        if os_name != "Windows": globals().get("tab").close()  # 关闭浏览器
