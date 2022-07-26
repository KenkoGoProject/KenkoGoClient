from module.global_dict import Global
from module.logger_ex import LoggerEx, LogLevel
from module.singleton_type import SingletonType
from module.yaml_config import YamlConfig


class UserConfig(metaclass=SingletonType):
    host = '127.0.0.1'  # 监听地址
    port = 18082  # 监听端口

    data: YamlConfig = {}

    def __init__(self, file_path):
        self.log = LoggerEx(self.__class__.__name__)
        self.file_path = file_path
        if Global().debug_mode:
            self.log.set_level(LogLevel.DEBUG)
        self.load()

    def load(self):
        self.log.debug(f'Loading config file: {self.file_path}')
        self.data = YamlConfig(self.file_path)

        # 读取配置
        self.port = int(self.data.get('port', self.port))
        self.host = str(self.data.get('host', self.host))

        # 若配置项不存在，则创建配置项
        # TODO: 写出时保留注释
        self.data.setdefault('port', self.port)
        self.data.setdefault('host', self.host)

        self.log.debug(f'Config loaded: {dict(self.data)}')

    def save(self):
        self.log.debug(f'Saving config file: {self.file_path}')
        self.data.save()
        self.log.debug(f'Config saved: {dict(self.data)}')
