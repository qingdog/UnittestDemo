## 单独安装浏览器/使用docker镜像
* https://playwright.dev/docs/browsers
```shell
npx playwright install --with-deps chromium
```
* https://playwright.dev/python/docs/docker
### 拉取镜像，root运行
```shell
docker pull mcr.microsoft.com/playwright/python:v1.47.0-noble
# 在受信任的网站上，您可以避免创建单独的用户，并使用 root，因为您信任将在浏览器上运行的代码。
docker run -it --rm --ipc=host mcr.microsoft.com/playwright/python:v1.47.0-noble /bin/bash
```
### 安全运行
```shell
docker run -it --rm --ipc=host --user pwuser --security-opt seccomp=seccomp_profile.json mcr.microsoft.com/playwright/python:v1.47.0-noble /bin/bash
```
---
在进行 Web 爬取（crawling）和数据抓取（scraping）时，确保系统的安全性和隔离性。
1. 使用不同的用户启动浏览器
在不受信任的网站上进行爬取时，为了提高安全性，建议使用与容器或主机系统中其他应用不同的用户来启动浏览器。这有助于防止潜在的安全漏洞，因为即使爬取过程中浏览器被攻击，攻击者的权限也会被限制在特定的用户范围内。
--user pwuser：指定容器中的用户（pwuser）来运行浏览器。
adduser：如果你在 Docker 容器中运行 Playwright，确保先创建一个新的用户（pwuser）。
3. Docker 命令
这个命令启动了一个基于 Playwright Docker 镜像的容器，并应用了以下选项：
-it：以交互模式运行容器，并连接到容器的终端。
--rm：容器退出后自动删除。
--ipc=host：将容器的 IPC（进程间通信）命名空间设置为主机系统，这样可以提高性能，特别是与浏览器相关的操作。
--user pwuser：容器中使用 pwuser 用户来启动应用。
--security-opt seccomp=seccomp_profile.json：将 seccomp_profile.json 安全配置文件应用于容器，限制容器中可调用的系统调用。
mcr.microsoft.com/playwright/python:v1.47.0-noble：指定 Playwright Python 的 Docker 镜像。
/bin/bash：容器启动时进入 Bash 终端。
4. seccomp 配置文件内容
seccomp 配置文件 seccomp_profile.json 定义了哪些操作可以在容器内执行，这里允许了创建用户命名空间的操作。它的内容如下：
```json
{
  "comment": "Allow create user namespaces",
  "names": [
    "clone",
    "setns",
    "unshare"
  ],
  "action": "SCMP_ACT_ALLOW",
  "args": [],
  "includes": {},
  "excludes": {}
}
```
"clone", "setns", "unshare"：这些系统调用与创建和管理进程的命名空间（namespace）相关，允许容器创建自己的用户空间，以提高隔离性。
"action": "SCMP_ACT_ALLOW"：表示允许这些操作。
2. 使用 seccomp（安全计算模式）配置文件
seccomp 是 Linux 内核的一项安全特性，允许你控制容器可以调用哪些系统调用。通过限制系统调用，可以大大减少容器中潜在的攻击面。
seccomp_profile.json 是一个用于配置 seccomp 策略的文件，它定义了哪些系统调用被允许执行。
你可以看到，seccomp_profile.json 中包括了 "clone", "setns", 和 "unshare" 这些特权操作，这些操作与创建和管理用户命名空间（user namespaces）有关。
---

### Centos7 Dockerfile
> 容器会运行 app.main，假设 main.py 是项目的入口点
> `/ms-playwright` 是chrome的安装目录
```shell
FROM public.ecr.aws/lambda/python:3.9

# to install requirements, if requirements are not there this can be removed
COPY requirements.txt ./
RUN pip install -r requirements.txt

# to install playwright on centos in a python image

# need to add playwright directory to env, so  that code can find it
ENV PLAYWRIGHT_BROWSERS_PATH=/ms-playwright

# install playwright
RUN python3 -m pip install playwright==1.30.0 -U
# install chromium browser binary
RUN python3 -m playwright install chromium

# install dependencies
RUN yum update -y && \
    yum install -y alsa-lib \
    at-spi2-atk  \
    at-spi2-core \
    atk \
    bash \
    cairo \
    cups-libs \
    dbus-libs \
    expat \
    flac-libs \
    gdk-pixbuf2 \
    glib2 \
    glibc \
    gtk3 \
    libX11 \
    libXcomposite \
    libXdamage \
    libXext \
    libXfixes \
    libXrandr \
    libXtst \
    libcanberra-gtk3 \
    libdrm \
    libgcc \
    libstdc++ \
    libxcb \
    libxkbcommon \
    libxshmfence \
    libxslt \
    mesa-libgbm \
    nspr \
    nss \
    nss-util \
    pango \
    policycoreutils \
    policycoreutils-python-utils \
    zlib

# copy source code if required
COPY app/ ./
CMD ["app.main"]
```

### 使用 Docker 的 挂载卷（Volumes）
挂载卷（Volumes）允许你将宿主机的文件夹与容器内的文件夹同步，这样你在宿主机上修改代码时，容器内的代码会自动同步更新，无需每次都重新复制代码。
步骤：
修改 Docker 启动命令，使用 -v 参数挂载本地代码目录到容器内的某个目录。例如，如果你的代码在宿主机的 ./app 文件夹中，可以这样运行容器：
```bash
docker run -v ./app:/app your_image_name
```
这里，./app 是宿主机上的代码目录，/app 是容器内的目标目录。当你在宿主机上修改代码时，容器内的 /app 目录会立即更新。
your_image_name 是启动镜像的名字
### main.py文件
```shell
project/
├── app/
│   ├── __init__.py
│   └── main.py
├── Dockerfile
└── requirements.txt
```
```python
# app/main.py
def main():
    print("Hello from the app!")

if __name__ == "__main__":
    main()
```
### 容器启动时运行 main.py 文件的 __main__ 函数
* CMD ["app.main"] -> CMD ["python3", "-m", "app.main"]
```shell
CMD ["python3", "-m", "app.main"]
```

### 运行
运行容器中的 Python 脚本（容器外部访问容器内的代码）
如果你希望在宿主机上执行 main.py，并且该文件位于 Docker 容器内，你可以选择以下几种方法：

方法 1：使用 Docker 容器的 docker exec 命令 运行 Python 脚本
你可以通过 docker exec 在正在运行的容器中执行命令，直接运行 main.py 脚本。

首先，查找容器 ID 或名称：
```bash
docker ps
```
然后，使用 docker exec 进入容器并运行 main.py：

```bash
docker exec -it <container_id_or_name> python3 /app/main.py
```
这里，<container_id_or_name> 是容器的 ID 或名称，/app/main.py 是容器内的 Python 脚本路径。