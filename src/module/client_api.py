import traceback

from module.global_dict import Global
from module.logger_ex import LoggerEx, LogLevel


class ClientApi:
    """Client API"""

    def __init__(self, name=None):
        self.name = name or traceback.extract_stack()[-2].name
        self.log = LoggerEx(f'{self.__class__.__name__} {name}')
        if Global().debug_mode:
            self.log.set_level(LogLevel.DEBUG)

    @staticmethod
    def get_info() -> dict:
        """获取Client的信息"""
        return {
            'app_name': Global().app_name,
            'version': Global().version_str,
            'connected': Global().kenko_go.websocket_connected,
            'websocket_msg_count': Global().websocket_message_count,
        }

    def disconnect(self) -> None:
        """断开连接"""
        self.log.debug('Disconnecting...')
        kenko_go = Global().kenko_go
        kenko_go.stop_websocket()
        self.log.debug('Disconnected.')

    def connect(self) -> None:
        """连接"""
        self.log.debug('Connecting...')
        kenko_go = Global().kenko_go
        kenko_go.start_websocket()
        self.log.debug('Connected.')
