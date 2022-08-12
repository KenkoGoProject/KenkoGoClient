from assets.cq_code import CqCode
from module.client_api import ClientApi
from module.global_dict import Global
from module.gocq_api import GocqApi
from module.logger_ex import LoggerEx, LogLevel
from module.message_config import MessageConfig
from module.server_api import ServerApi
from module.singleton_type import SingletonType

HELP_TEXT = f"""欢迎使用KenkoGo！

当前版本({Global().version_str})支持的命令：
!help - 显示帮助信息（即本信息）
!status - 显示当前状态（仅管理员）
!screen - 截屏（仅管理员）
"""


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
        if not self.enable:
            return self
        if message['post_type'] == 'message':
            return self.type_message(message)
        return True

    def type_message(self, message: dict) -> bool:
        msg = message['message'].strip()
        user_id = message['user_id']
        if self.config.block_self and user_id == message['self_id']:
            return False
        if msg == '!screen' and user_id in self.config.administrators:
            message['message'] = CqCode.image(get_screenshot())
            self.api.send_msg(message)
        if msg == '!status' and user_id in self.config.administrators:
            message['message'] = self.get_status()
            self.api.send_msg(message)
        if user_id in self.config.ignore_users:
            return True
        if user_id in self.config.block_users:
            self.log.debug(f'Message from blocked account {user_id}')
            return False

    def get_status(self) -> str:
        status = self.server.get_status()
        import json
        result = json.dumps(status, ensure_ascii=False, indent=4)
        status = self.client.get_info()
        result += '\n' + json.dumps(status, ensure_ascii=False, indent=4)
        return result


def get_screenshot() -> bytes:
    from io import BytesIO

    from PIL import ImageGrab
    with BytesIO() as f:
        ImageGrab.grab(all_screens=True).save(f, 'PNG')
        f.seek(0)
        return f.read()
