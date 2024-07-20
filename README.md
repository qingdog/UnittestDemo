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

```shell
# https://zh.wikipedia.org/wiki/Help:如何访问维基百科#本地反向代理
# git 不进行ssl证书认证
git config --global http.sslVerify false
# git当前仓库不认证
git config http.sslVerify false
# git执行命令时不认证
git -c http.sslVerify=false push

```

```shell
Package                Version
---------------------- --------
beautifulsoup4         4.12.3
bs4                    0.0.2
certifi                2024.6.2
cffi                   1.16.0
charset-normalizer     3.3.2
cli_helpers            2.3.1
click                  8.1.7
colorama               0.4.6
configobj              5.0.8
cryptography           36.0.2
ddt                    1.7.2
et-xmlfile             1.1.0
HTMLReport             2.4.0
HTMLTestRunner-Python3 0.8.0
idna                   3.7
jd-HTMLTestRunner      1.7.0
markdown-it-py         3.0.0
mdurl                  0.1.2
mycli                  1.27.0
openpyxl               3.1.5
pip                    24.1.2
pip-search             0.0.12
prompt-toolkit         3.0.43
pyaes                  1.6.1
pycparser              2.21
Pygments               2.17.2
PyMySQL                1.1.0
pyperclip              1.8.2
PyYAML                 6.0.1
requests               2.32.3
setuptools             49.2.1
soupsieve              2.5
sqlglot                22.5.0
sqlparse               0.4.4
tabulate               0.9.0
typing_extensions      4.12.2
unpack                 0.0.8
urllib3                2.2.2
wcwidth                0.2.13
xlrd                   1.2.0
```