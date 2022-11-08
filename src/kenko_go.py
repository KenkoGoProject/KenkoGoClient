import json
import time
from concurrent.futures import ThreadPoolExecutor
from threading import Thread
from typing import Optional, Union

from websocket import WebSocketApp

from assets.constants import (APP_DESCRIPTION, APP_NAME, VERSION_NUM,
                              VERSION_STR)
from module.database import Database
from module.global_dict import Global
from module.logger_ex import LoggerEx, LogLevel
from module.message_manager import MessageManager
from module.plugin_manager import PluginManager
from module.singleton_type import SingletonType
from module.user_config import UserConfig
from module.utils import kill_thread


class KenkoGo(metaclass=SingletonType):
    """主功能模块"""

    def __init__(self):
        self.log = LoggerEx(self.__class__.__name__)
        if Global().debug_mode:
            self.log.set_level(LogLevel.DEBUG)

        # 打印版本信息
        self.log.info(f'{APP_NAME} - {APP_DESCRIPTION}')
        self.log.info(f'Version: {VERSION_STR}')
        self.log.debug(f'Version Num: {VERSION_NUM}')

        self.user_config: UserConfig = Global().user_config  # 用户配置

        self.websocket_thread = None  # WebSocket 线程
        self.auto_reconnect = True  # 自动重连
        self.websocket_connected = False  # WebSocket 连接状态

        self.database = Database()  # 初始化数据库
        Global().database = self.database

        self.message_handle_thread_pool = ThreadPoolExecutor(None if self.user_config.multi_thread else 1)  # 消息处理线程池
        self.can_handle_message = False  # 是否可以处理消息
        self.message_manager = MessageManager()  # 消息管理器

        self.plugin_manager = PluginManager()  # 初始化插件管理器
        Global().plugin_manager = self.plugin_manager
        self.plugin_manager.load_config()  # 加载旧插件
        self.plugin_manager.load_local_modules()  # 加载新插件

        # 初始化 WebSocket 服务
        self.websocket_app = WebSocketApp(
            url=f'ws://{self.user_config.host}:{self.user_config.port}/client',
            header={'Authorization': f'Bearer {self.user_config.token}'},  # 鉴权
            on_open=self.__on_websocket_open,
            on_message=self.__on_websocket_message,
            on_error=self.__on_websocket_error,
            on_close=self.__on_websocket_close,
        )

    def start(self) -> None:
        """启动KenkoGo"""
        self.database.connect()  # 建立数据库连接
        if self.user_config.message_config.enable:
            self.message_manager.enable()
        self.plugin_manager.initialize_modules()  # 初始化插件
        self.plugin_manager.enable_plugins()  # 启用插件
        self.start_websocket()  # 启动WebSocket连接
        self.log.info('Started.')

    def stop(self) -> None:
        """停止KenkoGo"""
        self.log.debug(f'{APP_NAME} stopping.')
        self.message_manager.disable()
        self.plugin_manager.disable_all_plugin()  # 禁用插件
        self.stop_websocket()  # 停止WebSocket连接
        while self.can_handle_message is True:
            time.sleep(0.1)
        self.message_handle_thread_pool.shutdown()  # 等待消息处理线程池结束
        self.database.close()  # 断开数据库连接
        self.log.info('Stopped, see you next time.')

    def start_websocket(self) -> None:
        """启动WebSocket连接"""
        if self.websocket_app.keep_running:
            self.log.warning('WebSocket already started.')
            return
        self.websocket_thread = Thread(target=self.websocket_app.run_forever, daemon=True)  # 一个线程只能运行一次
        self.websocket_thread.start()

    def stop_websocket(self) -> None:
        """主动停止WebSocket连接"""
        self.auto_reconnect = False
        if self.websocket_app.keep_running:
            self.websocket_app.close()
            if self.websocket_app.keep_running:
                self.log.warning('WebSocket close failed. Try to stop it forcibly.')
                kill_thread(self.websocket_thread)
            else:
                self.log.debug('WebSocket close successfully.')
        else:
            self.log.warning('WebSocket may not start.')

    def __on_websocket_open(self, _) -> None:
        """WebSocket连接已启动"""
        self.websocket_connected = True
        self.auto_reconnect = True
        self.log.info('Connected to KenkoGoServer!')
        self.can_handle_message = True
        self.message_handle_thread_pool.submit(self.handle_event, 'connected')

    def __on_websocket_message(self, _, raw_message: Union[bytes, str]) -> None:
        """WebSocket收到消息

        :param raw_message: 消息内容，json格式
        """
        Global().websocket_message_count += 1
        if isinstance(raw_message, bytes):
            raw_message = raw_message.decode('utf-8').strip()  # 将bytes转换为str
        try:
            message: dict = json.loads(raw_message)
        except json.JSONDecodeError:
            # 如果不是JSON格式的消息，则直接忽略
            self.log.error(f'Received invalid message: {raw_message}')  # type: ignore[str-bytes-safe]
            return

        if message['post_type'] == 'server_event':
            if message['meta_event_type'] == 'gocq_event':
                self.log.info(f'Received gocq event: {message["message"]}')
        elif message['post_type'] == 'meta_event':
            if message['meta_event_type'] == 'heartbeat':
                ...  # 收到心跳消息，忽略
        else:
            # 其他消息，交由插件处理
            self.log.debug(f'Received message: {message}')  # type: ignore[str-bytes-safe]
            if self.can_handle_message is True:
                self.message_handle_thread_pool.submit(self.handle_event, 'message', message)

    def __on_websocket_error(self, _, error: Exception) -> None:
        """WebSocket连接发生错误

        :param error: 错误信息
        """
        if isinstance(error, ConnectionRefusedError):
            self.log.error(f'Connection refused: {error}')
            return
        self.log.exception(error)

    def __on_websocket_close(self, _, code: Optional[int], msg: Optional[str]) -> None:
        """WebSocket连接关闭

        :param code: 关闭代码
        :param msg: 关闭消息
        """
        self.websocket_app.close()
        self.log.debug(f'Disconnected from server: {code}, {msg}')
        if self.websocket_connected:  # 如果之前已经连接上了，就告诉插件
            self.message_handle_thread_pool.submit(self.handle_event, 'disconnected')
        self.websocket_connected = False
        self.can_handle_message = False
        if self.websocket_app.keep_running:
            self.log.warning('WebSocket close failed. Try to stop it forcibly.')
        if self.auto_reconnect:
            time.sleep(3)  # 等待3秒重连
            self.start_websocket()

    def handle_event(self, event: str, message: dict = None) -> None:
        """处理事件

        :param event: 事件类型
        :param message: 消息内容，仅当event为message时有效
        """
        if event == 'connected':
            if self.message_manager.on_connect() is not True:
                return
            self.plugin_manager.polling_connected()
        elif event == 'disconnected':
            if self.message_manager.on_disconnected() is not True:
                return
            self.plugin_manager.polling_disconnected()
        elif event == 'message':
            if self.message_manager.on_message(message) is not True:
                return
            self.plugin_manager.polling_message(message)
