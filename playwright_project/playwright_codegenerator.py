import json
import os
import subprocess
import shutil


def playwright_install():
    """构建软连接，安装浏览器和依赖"""
    # 目标和源路径
    link_target = r"C:\Users\Administrator\AppData\Local\ms-playwright\chromium-1155\chrome-win"
    link_source = r"C:\Program Files\Google\Chrome\Application"
    # 如果目标目录已存在，则删除
    if not os.path.exists(link_target):
        # shutil.rmtree(link_target)
        os.makedirs(os.path.dirname(link_target), exist_ok=True)
        # 运行 mklink 命令
        subprocess.run(f'cmd /c mklink /d "{link_target}" "{link_source}"', shell=True, check=True)
        print("符号链接创建成功！")
    # if not os.path.exists(r"C:\Program Files\Google\Chrome\Application\chrome_elf.dll"):
    if not os.path.exists(r"C:\Users\Administrator\AppData\Local\ms-playwright\chromium-1155\chrome-win\chrome_elf.dll"):
        subprocess.run(
            r'cmd /c mklink "C:\Program Files\Google\Chrome\Application\chrome_elf.dll" "C:\Program Files\Google\Chrome\Application\133.0.6943.99\chrome_elf.dll"',
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
    os.system("playwright codegen --load-storage=auth.json --color-scheme=dark baidu.com --save-storage=auth.json")


if __name__ == '__main__':
    playwright_install()
    # open_codegen_controls()
    playwright_codegen()
