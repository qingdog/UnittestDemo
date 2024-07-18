# start
```shell
PS D:\mytest\dyd\ddt_demo> tree /f .\BeautifulReport\
Folder PATH listing
Volume serial number is 00000041 CF0D:74A5
D:\MYTEST\DYD\DDT_DEMO\BEAUTIFULREPORT
│   BeautifulReport.py
│   README.md
│   __init__.py
│
├───template
│       template.html
│       theme.json
│       theme_candy.json
│       theme_cyan.json
│       theme_default.json
│       theme_memories.json
│
└───__pycache__
        BeautifulReport.cpython-312.pyc
        __init__.cpython-312.pyc

```
* template.html 模板文件不再使用cdn
* 通过 字体、图片的 Base64 编码的 DataURI 形式使用