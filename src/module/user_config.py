from assets.message_config import MessageConfig
from module.global_dict import Global
from module.logger_ex import LoggerEx, LogLevel
from module.singleton_type import SingletonType
from module.yaml_config import YamlConfig


class UserConfig(metaclass=SingletonType):
    host = '127.0.0.1'  # 监听地址
    port = 18082  # 监听端口
    token = ''  # api token
    message_config = MessageConfig()  # 消息管理器配置

    config_data: YamlConfig = {}

    def __init__(self, file_path):
        self.log = LoggerEx(self.__class__.__name__)
        self.file_path = file_path
        if Global().debug_mode:
            self.log.set_level(LogLevel.DEBUG)
        self.load()

    def load(self) -> None:
        self.log.debug(f'Loading config file: {self.file_path}')
        self.config_data = YamlConfig(self.file_path)
        need_save = len(self.config_data) == 0

        # 读取配置
        self.port = int(self.config_data.get('port', self.port))
        self.host = str(self.config_data.get('host', self.host))
        self.token = str(self.config_data.get('token', self.token))

        # 读取消息管理器配置
        t = dict(self.config_data.get('message_manager'))
        self.message_config.update(t)
        if len(t) < len(self.message_config):
            need_save = True

        # 若配置项不存在，则创建配置项
        self.config_data['port'] = self.port
        self.config_data['host'] = self.host
        self.config_data['token'] = self.token
        self.config_data['message_manager'] = self.message_config.to_dict()

        self.log.debug(f'Config loaded: {dict(self.config_data)}')
        if need_save:
            self.save()

    def save(self) -> None:
        self.log.debug(f'Saving config file: {self.file_path}')
        self.config_data.save()  # TODO: 写出时保留注释
        self.log.debug(f'Config saved: {dict(self.config_data)}')
