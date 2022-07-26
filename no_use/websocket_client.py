import json
from websocket import WebSocketApp

from module.global_dict import Global
from module.logger_ex import LoggerEx, LogLevel
from module.plugin_handler import PluginHandler
from module.singleton_type import SingletonType


class WebsocketClient(WebSocketApp, metaclass=SingletonType):
    def __init__(self):
        user_config = Global().user_config
        super().__init__(
            url=f'ws://{user_config.host}:{user_config.port}/client',
            header={
                'Authorization': 'Bearer None'
            },
            on_open=self.on_open,
            on_message=self.on_message,
            on_error=self.on_error,
            on_close=self.on_close,
            on_ping=self.on_ping,
            on_pong=self.on_pong,
            on_cont_message=self.on_cont_message,
            on_data=self.on_data,
        )
        self.log = LoggerEx(self.__class__.__name__)
        if Global().debug_mode:
            self.log.set_level(LogLevel.DEBUG)
        self.log.debug(f'{self.__class__.__name__} initializing...')
        self.plugin_handler = PluginHandler()

    def on_open(self, _):
        self.log.info('KenkoGoServer Connected!')

    def on_message(self, _, message):
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

    def on_error(self, _, error):
        self.log.error(error)

    def on_close(self, _, code, msg):
        self.log.debug(f'Disconnected from server: {code}, {msg}')

    def on_ping(self, _, data: bytes):
        # self.log.debug(f'Received ping: {data}')
        ...

    def on_pong(self, _):
        # self.log.debug('Received pong')
        ...

    def on_cont_message(self, _, message):
        self.log.debug(f'Received cont message: {message}')

    def on_data(self, _, data, type_, flag):
        # self.log.debug(f'Received data: {type_} {flag}')
        ...
