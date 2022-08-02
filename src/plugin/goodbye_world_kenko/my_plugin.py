from assets.simple_plugin import SimplePlugin
from module.client_api import ClientApi
from module.gocq_api import GocqApi
from module.server_api import ServerApi


class GoodbyeWorld(SimplePlugin):
    """你可以在继承SimplePlugin的情况下只保留__init__方法"""

    def __init__(self, api: GocqApi, client: ClientApi, server: ServerApi):
        super().__init__(api, client, server)
        self.api = api
        self.client = client
        self.server = server
        self.name = '再见，世界！'
        self.description = '插件也可以是一个包'
        self.version = '1.2.3'
