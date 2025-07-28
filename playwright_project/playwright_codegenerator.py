import json
import os
import subprocess
import shutil
import re

def get_version_directories(path=r"C:\Program Files\Google\Chrome\Application", pattern=r"^\d+\.\d+\.\d+\.\d+$"):  
    # 使用正则表达式来匹配版本号格式  
    version_pattern = re.compile(rf'{pattern}') 
    version_dirs = []  

    # 遍历指定路径下的所有目录  
    for item in os.listdir(path):  
        full_path = os.path.join(path, item)  
        # 检查是否是目录，并且是否符合版本号格式  
        if os.path.isdir(full_path) and version_pattern.match(item):  
            version_dirs.append(item)  
    
    if not version_dirs:
        return ""
    return version_dirs[0]

def playwright_install():
    """构建软连接，安装浏览器和依赖"""
    # like chromium-1155
    chromium_version = get_version_directories(path=r"C:\\Users\\Administrator\\AppData\\Local\\ms-playwright", pattern=r"^chromium-\d+$")
    # 目标和源路径
    link_target = rf"C:\Users\Administrator\AppData\Local\ms-playwright\{chromium_version}\chrome-win"
    link_source = r"C:\Program Files\Google\Chrome\Application"
    # 如果目标目录已存在，则删除
    if not os.path.exists(link_target):
        # shutil.rmtree(link_target)
        os.makedirs(os.path.dirname(link_target), exist_ok=True)
        # 运行 mklink 命令
        subprocess.run(f'cmd /c mklink /d "{link_target}" "{link_source}"', shell=True, check=True)
        print("chrome-win符号链接创建成功！")
    # if not os.path.exists(r"C:\Program Files\Google\Chrome\Application\chrome_elf.dll"):
    if not os.path.exists(rf"C:\Users\Administrator\AppData\Local\ms-playwright\{chromium_version}\chrome-win\\chrome_elf.dll"):
        subprocess.run(
            rf'cmd /c copy "C:\Program Files\Google\Chrome\Application\{get_version_directories()}\chrome_elf.dll" "C:\Program Files\Google\Chrome\Application\chrome_elf.dll"',
            shell=True, check=True)
        print("repair libraries: chrome_elf.dll")
    # 安装所有 chromium-1155,chromium_headless_shell-1155,ffmpeg-1011,firefox-1471,webkit-2123,winldd-1007
    # subprocess.run("playwright install", shell=True, check=True)


def open_codegen_controls():
    """在某些非标准设置中使用，打开一个带有 codegen 控件的单独窗口"""
    from playwright.sync_api import sync_playwright

    with sync_playwright() as p:
        # 确保以有头模式运行。
        browser = p.chromium.launch(headless=False)

        # 根据你的喜好设置上下文。
        context = browser.new_context()  # Pass any options
        context.route('**/*', lambda route: route.continue_())

        # 暂停页面，并手动开始录制。
        page = context.new_page()
        page.goto("https://www.baidu.com")
        page.pause()


def playwright_codegen():
    """playwright 代码生成器。可录制测试，然后将其复制到编辑器中"""
    if not os.path.exists("auth.json"):
        with open("auth.json", "w", encoding="utf-8") as file: file.write("{}")  # 写入空 JSON 对象
    os.system("playwright codegen --load-storage=auth.json --color-scheme=dark www.baidu.com --save-storage=auth.json")


if __name__ == '__main__':
    playwright_install()
    # open_codegen_controls()
    # `playwright codegen`
    playwright_codegen()
