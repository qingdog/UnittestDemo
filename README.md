# unittest demo

## 安装
* 安装依赖库
```shell
pip install -r requirements.txt
```

```shell
# 更新
python -m pip install --upgrade pip
# 安装搜索库
pip3 install pip_search
pip_search.exe htmltest -i https://pypi.tuna.tsinghua.edu.cn/simple
# 设置清华源
pip config set global.index-url https://pypi.tuna.tsinghua.edu.cn/simple

# 安装新版本312废弃的distutils
pip install setuptools
# 安装unittest的可多线程测试报告
pip install htmlreport
# 安装操作excel库
pip install -i https://pypi.tuna.tsinghua.edu.cn/simple openpyxl
# 带截图，饼图，折线图，历史结果查看的测试报告
https://github.com/githublitao/HTMLTestRunner_Chart
```

```shell
# 集成邮件/钉钉/企微/飞书 发送消息。
pip install XTestRunner
* https://github.com/SeldomQA/XTestRunner

pip install seldom==3.7.0
# https://seldomqa.github.io/getting-started/data_driver.html#data-方法
https://seldomqa.github.io/getting-started/quick_start.html#多线程运行
```

### 安装旧版本
```shell
#卸载已安装的
pip uninstall xlrd 
#下载对应的版本
pip install xlrd==1.2.0
```

### git操作

```shell
# https://zh.wikipedia.org/wiki/Help:如何访问维基百科#本地反向代理
# git 不进行ssl证书认证
git config --global http.sslVerify false
# git当前仓库不认证
git config http.sslVerify false
# git执行命令时不认证
git -c http.sslVerify=false push
```
> 控制面板\所有控制面板项\凭据管理器
```shell
cat .\.gitconfig
[user]
        email = qingdoor@gmail.com
        name = qingdog
[credential "https://github.com"]
        provider = generic
[http]
	sslVerify = false
```
```shell
wget https://github.com/mashirozx/Pixiv-Nginx --no-check-certificate
--2024-07-24 10:30:46--  https://github.com/mashirozx/Pixiv-Nginx
正在解析主机 github.com (github.com)... 127.0.0.1
正在连接 github.com (github.com)|127.0.0.1|:443... 已连接。
警告: “github.com” 的证书不可信。
警告: “github.com” 的证书颁发者未知。
证书所有者与主机名 “github.com” 不符
已发出 HTTP 请求，正在等待回应... 200 OK
长度：未指定 [text/html]
正在保存至: “Pixiv-Nginx”

Pixiv-Nginx                                              [ <=>                                                                                                                 ] 344.11K  1.96MB/s  用时 0.2s

2024-07-24 10:30:48 (1.96 MB/s) - “Pixiv-Nginx” 已保存 [352364]
```

### 运行loguru_demo

```shell
cd "D:\mytest\UnittestDemo"
python
exec(open("./logs/loguru_demo.py", encoding="utf-8").read())
```

```shell
pip install python-dotenv
```
```python
from dotenv import load_dotenv
load_dotenv()

TELEGRAM_BOT_TOKEN = os.getenv('TELEGRAM_BOT_TOKEN')
```
* 更新包
```shell
pip install XTestRunner==1.7.5 --index-url https://pypi.org/simple
```
### playwright 自动录制操作（生成代码）
* 设置playwright浏览器 `playwright install`
```shell
mkdir C:\Users\Administrator\AppData\Local\ms-playwright\chromium-1140\
# 创建浏览器所在目录（文件夹）的符号链接
cmd /c mklink /d "C:\Users\Administrator\AppData\Local\ms-playwright\chromium-1140\chrome-win\" "C:\Program Files\Google\Chrome\Application\"
# touch 'C:\Users\Administrator\AppData\Local\ms-playwright\chromium-1140\DEPENDENCIES_VALIDATED'
playwright codegen demo.playwright.dev/todomvc
# playwright codegen --timezone="Asia/Shanghai" --geolocation="31.235564,121.481099" --lang="zh-CN" --color-scheme=dark --save-storage=auth.json bing.com/maps
# playwright codegen --load-storage=auth.json github.com/microsoft/playwright
```
### playwright 生成报告
* 安装依赖
```shell
pip install pytest pytest-playwright allure-pytest
npm install -g allure-commandline # 安装 Allure 命令行工具
ls $(npm config get prefix) -r allure.* # 查看安装位置
```

* shell执行

```shell
# 生成测试结果（allure-results）
pytest --alluredir=allure-results
# 生成多页面报告（allure-results）
allure generate allure-results --clean
# allure open allure-report # 打开报告

# 生成单页面报告（allure-results）
allure generate --single-file allure-results --clean
```
* python执行
```python
import os
# 设置 - Python 集成工具 - 默认测试运行程序 Unittest
os.system("pytest --alluredir=allure-results")
os.system("allure generate --single-file allure-results --clean")
```