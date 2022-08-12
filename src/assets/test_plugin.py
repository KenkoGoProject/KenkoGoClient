from assets.simple_plugin import SimplePlugin
from module.client_api import ClientApi
from module.gocq_api import GocqApi
from module.server_api import ServerApi


class TestPlugin(SimplePlugin):
    def __init__(self, api: GocqApi, client: ClientApi, server: ServerApi):
        super().__init__(api, client, server)
        self.api = api
        self.client = client
        self.server = server
        self.name = '测试插件'
        self.description = '该插件仅作调试用处'
        self.version = 'Test Only'

    def on_message(self, message: dict) -> bool:
        if message['post_type'] == 'message':
            msg: str = message['raw_message']
            import re
            if msg == 'tsa1':
                from assets.cq_code import CqCode
                message['message'] = CqCode.record_local('dyy.mp3')
                self.api.send_msg(message)
        return True  # 返回True表示消息将被传递给下一个插件，否则表示消息被拦截
