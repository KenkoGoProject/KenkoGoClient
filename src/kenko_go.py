import json
import time

from websocket import WebSocketApp

from module.database import Database
from module.global_dict import Global
from module.logger_ex import LoggerEx, LogLevel
from module.plugin_manager import PluginManager
from module.singleton_type import SingletonType
from module.thread_ex import ThreadEx


class KenkoGo(metaclass=SingletonType):
    """主功能模块"""

    def __init__(self):
        self.log = LoggerEx(self.__class__.__name__)
        if Global().debug_mode:
            self.log.set_level(LogLevel.DEBUG)

        # 打印版本信息
        self.log.info(f'{Global().app_name} - {Global().description}')
        self.log.info(f'Version: {Global().version_str}')
        self.log.debug(f'Version Num: {Global().version_num}')

        self.websocket_thread = None  # WebSocket 线程
        self.auto_reconnect = True  # 自动重连
        self.websocket_connected = False  # WebSocket 连接状态

        Global().database = Database()  # 初始化数据库
        Global().plugin_manager = PluginManager()  # 初始化插件管理器
        Global().plugin_manager.load_config()  # 加载旧插件
        Global().plugin_manager.load_local_modules()  # 加载新插件

        # 初始化 WebSocket 服务
        user_config = Global().user_config
        self.websocket_app = WebSocketApp(
            url=f'ws://{user_config.host}:{user_config.port}/client',
            header={'Authorization': 'Bearer None'},  # 鉴权
            on_open=self.__on_websocket_open,
            on_message=self.__on_websocket_message,
            on_error=self.__on_websocket_error,
            on_close=self.__on_websocket_close,
            on_data=self.__on_websocket_data,
        )

    def start(self) -> None:
        """启动KenkoGo"""
        Global().database.connect()  # 建立数据库连接
        Global().plugin_manager.initialize_modules()  # 初始化插件
        Global().plugin_manager.enable_plugins()  # 启用插件
        self.start_websocket()  # 启动WebSocket连接
        self.log.info(f'{Global().app_name} started.')

    def stop(self) -> None:
        """停止KenkoGo"""
        self.log.debug(f'{Global().app_name} stopping.')
        Global().plugin_manager.disable_all_plugin()  # 禁用插件
        self.stop_websocket()  # 停止WebSocket连接
        Global().database.disconnect()  # 断开数据库连接
        self.log.info(f'{Global().app_name} stopped, see you next time.')

    def start_websocket(self) -> None:
        """启动WebSocket连接"""
        if self.websocket_app.keep_running:
            self.log.warning('WebSocket already started.')
            return
        self.websocket_thread = ThreadEx(target=self.websocket_app.run_forever, daemon=True)  # 一个线程只能运行一次
        self.websocket_thread.start()

    def stop_websocket(self) -> None:
        """主动停止WebSocket连接"""
        self.auto_reconnect = False
        if self.websocket_app.keep_running:
            self.websocket_app.close()
            if self.websocket_app.keep_running:
                self.log.warning('WebSocket close failed. Try to stop it forcibly.')
                self.websocket_thread.kill()
            else:
                self.log.debug('WebSocket close successfully.')
        else:
            self.log.warning('WebSocket may not start.')

    def __on_websocket_open(self, _) -> None:
        """WebSocket连接已启动"""
        self.websocket_connected = True
        self.auto_reconnect = True
        self.log.info('KenkoGoServer Connected!')
        Global().plugin_manager.polling_event('connected')

    def __on_websocket_message(self, _, message) -> None:
        """WebSocket收到消息"""
        if isinstance(message, bytes):
            message = message.decode('utf-8').strip()  # 将bytes转换为str
        try:
            message = json.loads(message)
        except json.JSONDecodeError:
            # 如果不是JSON格式的消息，则直接忽略
            self.log.error(f'Received invalid message: {message}')
            return

        if message['post_type'] == 'server_event':
            if message['meta_event_type'] == 'gocq_event':
                self.log.info(f'Received gocq event: {message["message"]}')
        elif message['post_type'] == 'meta_event':
            if message['meta_event_type'] == 'heartbeat':
                # 收到心跳消息，忽略
                ...
        else:
            # 其他消息，交由插件处理
            self.log.debug(f'Received message: {message}')
            Global().plugin_manager.polling_event('message', message)

    def __on_websocket_error(self, _, error) -> None:
        """WebSocket连接发生错误"""
        self.log.error(f'WebSocket Error: {error}')

    def __on_websocket_close(self, _, code, msg) -> None:
        """WebSocket连接关闭"""
        self.websocket_app.close()
        self.log.debug(f'Disconnected from server: {code}, {msg}')
        if self.websocket_connected:  # 如果之前已经连接上了，就告诉插件
            Global().plugin_manager.polling_event('disconnected')
        self.websocket_connected = False
        if self.websocket_app.keep_running:
            self.log.warning('WebSocket close failed. Try to stop it forcibly.')
        if self.auto_reconnect:
            time.sleep(3)  # 等待3秒重连
            self.start_websocket()

    @staticmethod
    def __on_websocket_data(*_) -> None:
        Global().websocket_message_count += 1
