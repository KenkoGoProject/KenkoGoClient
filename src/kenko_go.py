from assets.server_status import ServerStatus
from module.exception_ex import PortInUseError
from module.global_dict import Global
from module.logger_ex import LoggerEx, LogLevel
from module.thread_ex import ThreadEx
from module.utils import is_port_in_use


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

    def start(self):
        """启动WebSocket服务"""

        # self.http_thread = ThreadEx(
        #     target=uvicorn.run,
        #     daemon=True,
        #     kwargs={
        #         'app': HttpServer(),
        #         'host': Global().user_config.host,
        #         'port': Global().user_config.port,
        #         'log_level': 'warning' if Global().debug_mode else 'critical',
        #     }
        # )
        # self.http_thread.start()
        self._status = ServerStatus.HTTP_THREAD_STARTED
        self.log.info(f'{Global().app_name} started.')

    def stop(self):
        """停止WebSocket服务"""
        self.log.debug(f'{Global().app_name} stopping.')
        if self._status != ServerStatus.STOPPED and isinstance(self.http_thread, ThreadEx):
            # TODO: 实现优雅的关闭
            self.http_thread.kill()
            self._status = ServerStatus.STOPPED
        self.log.info(f'{Global().app_name} stopped, see you next time.')
