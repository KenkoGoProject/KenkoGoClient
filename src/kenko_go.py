import time

from module.thread_ex import ThreadEx
import json
from websocket import WebSocketApp

from module.global_dict import Global
from module.logger_ex import LoggerEx, LogLevel
from module.plugin_handler import PluginHandler
from module.singleton_type import SingletonType


class KenkoGo(metaclass=SingletonType):
    """主功能模块"""

    def __init__(self):
        self.log = LoggerEx(self.__class__.__name__)
        if Global().debug_mode:
            self.log.set_level(LogLevel.DEBUG)
        self.http_thread = None

        # 打印版本信息
        self.log.info(f'{Global().app_name} - {Global().description}')
        self.log.info(f'Version: {Global().version_str}')
        self.log.debug(f'Version Num: {Global().version_num}')

        self.plugin_handler = PluginHandler()  # 初始化插件管理器
        self.plugin_handler.load_plugins()  # 加载插件

        # 初始化 WebSocket 服务
        user_config = Global().user_config
        self.websocket_app = WebSocketApp(
            url=f'ws://{user_config.host}:{user_config.port}/client',
            header={
                'Authorization': 'Bearer None'
            },
            on_open=self.__on_websocket_open,
            on_message=self.__on_websocket_message,
            on_error=self.__on_websocket_error,
            on_close=self.__on_websocket_close,
            on_ping=self.__on_websocket_ping,
            on_pong=self.__on_websocket_pong,
            on_cont_message=self.__on_websocket_cont_message,
            on_data=self.__on_websocket_data,
        )

    def start(self):
        """启动插件与WebSocket连接"""
        self.plugin_handler.enable_plugins()  # 启用插件
        self.__start_websocket_thread()  # 启动WebSocket连接
        self.log.info(f'{Global().app_name} started.')

    def __start_websocket_thread(self):
        self.http_thread = ThreadEx(
            target=self.websocket_app.run_forever,
            daemon=True,
        )
        self.http_thread.start()

    def stop(self):
        """停止WebSocket服务"""
        self.log.debug(f'{Global().app_name} stopping.')
        self.plugin_handler.disable_plugins()
        if isinstance(self.http_thread, ThreadEx):
            # TODO: 实现优雅的关闭
            self.http_thread.kill()
        self.log.info(f'{Global().app_name} stopped, see you next time.')

    def __on_websocket_open(self, _):
        self.log.info('KenkoGoServer Connected!')

    def __on_websocket_message(self, _, message):
        if isinstance(message, bytes):
            message = message.decode('utf-8')
        message = json.loads(message)

        if message['post_type'] == 'meta_event':
            if message['meta_event_type'] == 'heartbeat':
                self.log.debug('Received heartbeat')
        else:
            self.log.debug(f'Received message: {message}')
            if self.plugin_handler.plugins_loaded:
                self.plugin_handler.broadcast_message(message)

    def __on_websocket_error(self, _, error):
        self.log.error(error)

    def __on_websocket_close(self, _, code, msg):
        self.log.debug(f'Disconnected from server: {code}, {msg}')
        time.sleep(3)
        self.__start_websocket_thread()

    def __on_websocket_ping(self, _, data: bytes):
        # self.log.debug(f'Received ping: {data}')
        ...

    def __on_websocket_pong(self, _):
        # self.log.debug('Received pong')
        ...

    def __on_websocket_cont_message(self, _, message):
        self.log.debug(f'Received cont message: {message}')

    def __on_websocket_data(self, _, data, type_, flag):
        # self.log.debug(f'Received data: {type_} {flag}')
        ...
