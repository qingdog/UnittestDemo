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

### 运行loguru_demo

```shell
cd "D:\mytest\UnittestDemo"
python
exec(open("./logs/loguru_demo.py", encoding="utf-8").read())
```

```shell
pip list
Package                   Version
------------------------- -----------
aiomysql                  0.2.0
Appium-Python-Client      3.2.1
asyncpg                   0.29.0
attrs                     23.2.0
BeautifulReport           0.1.3
beautifulsoup4            4.12.3
bs4                       0.0.2
certifi                   2024.6.2
cffi                      1.16.0
charset-normalizer        3.3.2
cli_helpers               2.3.1
click                     8.1.7
colorama                  0.4.6
configobj                 5.0.8
cryptography              42.0.8
ddt                       1.7.2
distlib                   0.3.8
et-xmlfile                1.1.0
filelock                  3.15.4
genson                    1.2.2
h11                       0.14.0
HTMLReport                2.4.0
idna                      3.7
jd-HTMLTestRunner         1.7.0
Jinja2                    3.1.4
jmespath                  0.10.0
jsonschema                4.23.0
jsonschema-specifications 2023.12.1
loguru                    0.6.0
markdown-it-py            3.0.0
MarkupSafe                2.1.5
mdurl                     0.1.2
mycli                     1.27.2
openpyxl                  3.1.5
outcome                   1.3.0.post0
pip                       24.1.2
pip-search                0.0.12
pipenv                    2024.0.1
platformdirs              4.2.2
prompt_toolkit            3.0.47
pyaes                     1.6.1
pycparser                 2.22
Pygments                  2.18.0
PyMySQL                   1.1.1
pyperclip                 1.9.0
PySocks                   1.7.1
python-dateutil           2.8.2
PyYAML                    6.0.1
referencing               0.35.1
requests                  2.32.3
rich                      13.7.1
rpds-py                   0.19.0
seldom                    3.7.0
selenium                  4.21.0
setuptools                70.1.1
six                       1.16.0
sniffio                   1.3.1
sortedcontainers          2.4.0
soupsieve                 2.5
sqlglot                   25.5.1
sqlparse                  0.4.4
tabulate                  0.9.0
trio                      0.26.0
trio-websocket            0.11.1
typing_extensions         4.12.2
urllib3                   2.2.2
virtualenv                20.26.3
wcwidth                   0.2.13
websocket-client          1.7.0
win32-setctime            1.1.0
wsproto                   1.2.0
XTestRunner               1.7.4
```