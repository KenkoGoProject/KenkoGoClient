import sys
from pathlib import Path

from module.client_api import ClientApi
from module.gocq_api import GocqApi
from module.logger_ex import LoggerEx
from module.server_api import ServerApi

PLUGIN_CLASS = 'SimplePlugin'


class SimplePlugin:
    """这是插件模板"""

    PLUGIN_NAME = ''  # 插件名称
    PLUGIN_DESCRIPTION = ''  # 插件描述
    PLUGIN_VERSION = '#ERROR#'  # 插件版本

    PLUGIN_DESCRIPTION_LONG = ''  # 长描述，用于插件详情页
    PLUGIN_AUTHOR = ''  # 插件作者
    PLUGIN_HELP_TEXT = ''  # 插件帮助文本
    PLUGIN_LINK = ''  # 插件链接

    def __init__(self, api: GocqApi, client: ClientApi, server: ServerApi):
        """实例初始化

        此处仅用作初始化插件信息，你可以在这里初始化一些依赖
        """
        self.api: GocqApi = api
        self.client: ClientApi = client
        self.server: ServerApi = server
        self.logger: LoggerEx = client.logger
        self.path = Path(__file__).parent.absolute()
        sys.path.append(str(self.path))

    def on_enable(self):
        """插件被启用"""
        return self  # 务必返回self

    def on_before_disable(self):
        """插件将被禁用，你还可以处理一些事情"""
        return self  # 务必返回self

    def on_disable(self):
        """插件已被禁用，可以用于清理一些资源"""
        return self  # 务必返回self

    def on_connect(self):
        """已连接到KenkoGo服务器"""
        return self  # 务必返回self

    def on_disconnect(self):
        """已断开服务器连接"""
        return self  # 务必返回self

    def on_message(self, message: dict):
        """收到 go-cqhttp 消息"""
        return True  # 返回True表示消息将被传递给下一个插件，返回False表示消息被拦截
