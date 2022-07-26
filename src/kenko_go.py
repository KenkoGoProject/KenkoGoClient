from assets.server_status import ServerStatus
from module.global_dict import Global
from module.logger_ex import LoggerEx, LogLevel
from module.plugin_handler import PluginHandler
from module.thread_ex import ThreadEx
from module.websocket_client import WebsocketClient


class KenkoGo:
    """主功能模块"""
    _status: ServerStatus = ServerStatus.STOPPED

    def __init__(self):
        self.log = LoggerEx(self.__class__.__name__)
        if Global().debug_mode:
            self.log.set_level(LogLevel.DEBUG)
        self.http_thread = None

        # 打印版本信息
        self.log.info(f'{Global().app_name} - {Global().description}')
        self.log.info(f'Version: {Global().version_str}')
        self.log.debug(f'Version Num: {Global().version_num}')

        self.plugin_handler = PluginHandler()

    def start(self):
        """启动WebSocket服务"""

        self.http_thread = ThreadEx(
            target=WebsocketClient().run_forever,
            daemon=True,
            kwargs={}
        )
        self.http_thread.start()

        self.plugin_handler.load_plugins()
        self.plugin_handler.enable_plugins()

        self._status = ServerStatus.HTTP_THREAD_STARTED
        self.log.info(f'{Global().app_name} started.')

    def stop(self):
        """停止WebSocket服务"""
        self.log.debug(f'{Global().app_name} stopping.')
        self.plugin_handler.disable_plugins()
        if self._status != ServerStatus.STOPPED and isinstance(self.http_thread, ThreadEx):
            # TODO: 实现优雅的关闭
            self.http_thread.kill()
            self._status = ServerStatus.STOPPED
        self.log.info(f'{Global().app_name} stopped, see you next time.')
