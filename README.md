# KenkoGoClient

![Python Version](https://img.shields.io/badge/python-3.9.13-blue)
![License](https://img.shields.io/github/license/AkagiYui/KenkoGoClient)
![GitHub commit activity](https://img.shields.io/github/commit-activity/m/AkagiYui/KenkoGoClient)

A Client of [KenkoGoServer](https://github.com/AkagiYui/KenkoGoServer)

## 功能介绍 Introduction

该项目只是一个简单的 HTTP 与 WebSocket 客户端，你也可以编写属于你的 KenkoGoClient，
或者使用[Web版](https://kenkogo.akagiyui.com) [kenkogo-webui](https://github.com/AkagiYui/kenkogo-webui)

不过还是建议使用 [NoneBot2](https://v2.nonebot.dev/) 等功能更完善的客户端。

## 快速开始 Quick Start

1. 在 [release](https://github.com/AkagiYui/KenkoGoClient/releases) 下载最新版本并解压

```shell
chmod +x ./kenkogo  # 赋予执行权限
vim config.yaml  # 修改配置文件
./kenkogo --debug
```

> 命令行参数说明
> 
> --debug: 开启调试模式，将输出更多信息

当控制台提示`KenkoGo Started`时，可输入`/help`查看可用的指令。


## 更新日志 [Changelog](Changelog.md)


## 注意事项 Tips

该项目尚未成熟，`master`分支仍处于开发阶段，请勿在生产环境使用。

该项目是我的第一个 Python 项目，代码中可能存在大量错误或不规范的地方，有任何问题请在 issues 上提出，以帮助我进步，谢谢。

该项目未计划支持 Windows 10 以下版本的系统，并且非 amd64 架构的系统暂未经过测试。

## 开发相关 Development

操作系统：[Windows 10 19044.1586](https://www.microsoft.com/zh-cn/windows)

系统架构：amd64

### 使用技术 Technology Stack

Python: [3.9.13](https://www.python.org/) [下载地址](https://www.python.org/downloads/release/python-3913/)

构建工具: [Nuitka](https://nuitka.net/) [下载地址](https://nuitka.net/doc/download.html)

数据库: [SQLite](https://www.sqlite.org/index.html)

自动构建: [GitHub Actions](https://https://docs.github.com/cn/actions)

依赖表生成工具: [pip-tools 6.8.0](https://github.com/jazzband/pip-tools/)

导入排序工具: [isort 5.10.1](https://pycqa.github.io/isort/)

代码格式化工具: [flake8 4.0.1](https://flake8.readthedocs.io/en/latest/) [mypy 0.971](https://mypy.readthedocs.io/en/latest/)

### 运行时Python包  Runtime Python Package

- [rich 12.5.1](https://github.com/Textualize/rich/blob/master/README.cn.md) 控制台美化工具
- [ruamel.yaml 0.17.21](https://yaml.readthedocs.io/en/latest/) Yaml解析工具
- [requests 2.28.1](https://requests.readthedocs.io/en/latest/) HTTP客户端
- [websockets-client 1.3.3](https://github.com/websocket-client/websocket-client) Websocket 客户端
- [inflection 0.5.1](https://github.com/jpvanhal/inflection) 字符串格式化工具
- [qrcode 7.3.1](https://github.com/lincolnloop/python-qrcode) 二维码生成工具
- [pyzbar 0.1.9](https://pypi.org/project/pyzbar/) 二维码识别工具
- [Pillow 9.2.0](https://python-pillow.org/) 图像处理工具

### 待办事项 Todo

- [ ] 集成 [Socket.IO](https://github.com/miguelgrinberg/python-socketio)
- [ ] 集成 [distro](https://github.com/python-distro/distro) 系统平台信息获取工具
- [ ] 集成 [pydis](https://github.com/Zombie123456/pydis)
- [ ] 集成 [retrying](https://github.com/rholder/retrying)
- [ ] 编写 Nuitka 脚本

## 从代码开始 Start from Code

### 运行 Start

请确保你的机器有 **Python 3.9.13** 的环境，其他版本未经测试。

1. 部署运行环境

```shell
git clone https://github.com/AkagiYui/KenkoGoClient
cd ./KenkoGoClient
python -m venv venv
./venv/Scripts/activate
python -m pip install -r ./requirements.txt
```

2. 修改配置文件

```shell
cd ./src
cp config.yaml.bak config.yaml
```

3. 启动脚本

```shell
python ./main.py --debug
```

### 代码检查 Code Lint

```shell
python -m pip install -r ./requirements-dev.txt
python ./code_lint.py
```

### 构建 Build

```shell
python -m pip install -r ./requirements-build.txt
python ./build.py
```
