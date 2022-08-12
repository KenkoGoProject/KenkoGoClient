from assets.message_config import MessageConfig
from module.client_api import ClientApi
from module.global_dict import Global
from module.gocq_api import GocqApi
from module.logger_ex import LoggerEx, LogLevel
from module.server_api import ServerApi
from module.singleton_type import SingletonType


class MessageManager(metaclass=SingletonType):
    """消息管理器，用于处理 go-cqhttp 消息"""

    def __init__(self):
        """初始化"""

        self.log = LoggerEx(self.__class__.__name__)
        if Global().debug_mode:
            self.log.set_level(LogLevel.DEBUG)

        self.enable = False

        user_config = Global().user_config
        host_and_port = f'{user_config.host}:{user_config.port}'
        token = user_config.token

        self.api = GocqApi(host_and_port, token, self.__class__.__name__)
        self.client = ClientApi(self.__class__.__name__)
        self.server = ServerApi(host_and_port, token, self.__class__.__name__)
        self.name = 'MessageManager/'
        self.description = '内置的消息管理器'
        self.description_long = f'{self.description}，可用于处理一些基本的事件。\n如：好友请求'
        self.author = 'AkagiYui'

        self.config: MessageConfig = user_config.message_config
        self.log.print_object(self.config.to_dict())

    def on_initialize(self):
        """插件初始化"""
        self.log.debug('MessageManager initialized')
        return self

    def on_enable(self):
        """插件被启用"""
        self.enable = True
        self.log.debug('MessageManager enabled')
        return self

    def on_connect(self):
        """已连接到KenkoGo服务器"""
        ...
        return self

    def on_disconnect(self):
        """已断开服务器连接"""
        ...
        return self

    def on_message(self, message: dict):
        """收到 go-cqhttp 消息"""
        if message['post_type'] == 'message':
            user_id = message['user_id']
            if self.config.block_self and user_id == message['self_id']:
                return False
            if user_id in self.config.ignore_users:
                self.log.debug(f'Ignore message from {user_id}')
                return True
            if user_id in self.config.block_users:
                self.log.debug(f'Message from blocked account {user_id}')
                return False
        return True
