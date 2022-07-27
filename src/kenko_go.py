import json
import time

from websocket import WebSocketApp

from module.global_dict import Global
from module.logger_ex import LoggerEx, LogLevel
from module.plugin_handler import PluginHandler
from module.singleton_type import SingletonType
from module.thread_ex import ThreadEx


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
                'Authorization': 'Bearer None'  # TODO: 鉴权
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
        self.websocket_connected = False

    def start(self):
        """启动插件与WebSocket连接"""
        self.plugin_handler.enable_all_plugin()  # 启用插件
        self.__start_websocket_thread()  # 启动WebSocket连接
        self.log.info(f'{Global().app_name} started.')

    def __start_websocket_thread(self):
        self.http_thread = ThreadEx(
            target=self.websocket_app.run_forever,
            daemon=True,
        )
        self.http_thread.start()

    def stop(self):
        """停止所有插件与WebSocket连接"""
        self.log.debug(f'{Global().app_name} stopping.')
        self.plugin_handler.disable_all_plugin()
        if isinstance(self.http_thread, ThreadEx):
            # TODO: 实现优雅的关闭
            self.http_thread.kill()
        self.log.info(f'{Global().app_name} stopped, see you next time.')

    def __on_websocket_open(self, _):
        self.websocket_connected = True
        self.log.info('KenkoGoServer Connected!')
        self.plugin_handler.broadcast_event('connected')

    def __on_websocket_message(self, _, message):
        if isinstance(message, bytes):
            message = message.decode('utf-8').strip()
        try:
            message = json.loads(message)
        except json.JSONDecodeError:
            self.log.error(f'Received invalid message: {message}')
            return

        if message['post_type'] == 'meta_event':
            if message['meta_event_type'] == 'heartbeat':
                # self.log.debug('Received heartbeat')
                ...
        else:
            self.log.debug(f'Received message: {message}')
            self.plugin_handler.broadcast_event('message', message)

    def __on_websocket_error(self, _, error):
        self.log.error(error)

    def __on_websocket_close(self, _, code, msg):
        self.log.debug(f'Disconnected from server: {code}, {msg}')
        if self.websocket_connected:
            self.plugin_handler.broadcast_event('disconnected')
        self.websocket_connected = False
        time.sleep(3)
        self.__start_websocket_thread()

    def __on_websocket_ping(self, _, data: bytes):
        # self.log.debug(f'Received ping: {data}')
        ...

    def __on_websocket_pong(self, _):
        self.log.debug('Received pong')
        ...

    def __on_websocket_cont_message(self, _, message):
        self.log.debug(f'Received cont message: {message}')

    def __on_websocket_data(self, _, data, type_, flag):
        # self.log.debug(f'Received data: {type_} {flag}')
        ...
