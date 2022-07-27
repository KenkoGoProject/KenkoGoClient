from assets.cq_code import CqCode
from assets.simple_plugin import SimplePlugin
from module.client_api import ClientApi
from module.gocq_api import GocqApi
from module.server_api import ServerApi


class GoodbyeWorld(SimplePlugin):
    """你可以继承 SimplePlugin 以省略一些方法"""
    def __init__(self, api: GocqApi, client: ClientApi, server: ServerApi):
        """实例初始化

        此处仅用作初始化插件信息，建议不要处理其他代码，以免发生异常情况
        """
        super().__init__(api, client, server)
        self.api = api
        self.client = client
        self.server = server
        self.name = '再见，世界！'
        self.description = '这还是一个插件示例'
        self.version = '1.2.3'

    def on_message(self, message: dict) -> bool:
        """收到 go-cqhttp 消息

        遵循 go-cqhttp 版的 OneBot 消息格式
        """
        return True  # 返回True表示消息将被传递给下一个插件，否则表示消息被拦截
