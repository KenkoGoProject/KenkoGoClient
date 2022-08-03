from module.global_dict import Global
from module.logger_ex import LoggerEx, LogLevel
from module.singleton_type import SingletonType
from module.yaml_config import YamlConfig


class UserConfig(metaclass=SingletonType):
    host = '127.0.0.1'  # 监听地址
    port = 18082  # 监听端口
    token = ''  # api token

    data: YamlConfig = {}

    def __init__(self, file_path):
        self.log = LoggerEx(self.__class__.__name__)
        self.file_path = file_path
        if Global().debug_mode:
            self.log.set_level(LogLevel.DEBUG)
        self.load()

    def load(self) -> None:
        self.log.debug(f'Loading config file: {self.file_path}')
        self.data = YamlConfig(self.file_path)
        need_save = len(self.data) == 0

        # 读取配置
        self.port = int(self.data.get('port', self.port))
        self.host = str(self.data.get('host', self.host))
        self.token = str(self.data.get('token', self.token))

        # 若配置项不存在，则创建配置项
        self.data.setdefault('port', self.port)
        self.data.setdefault('host', self.host)
        self.data.setdefault('token', self.token)

        self.log.debug(f'Config loaded: {dict(self.data)}')
        if need_save:
            self.save()

    def save(self) -> None:
        self.log.debug(f'Saving config file: {self.file_path}')
        self.data.save()  # TODO: 写出时保留注释
        self.log.debug(f'Config saved: {dict(self.data)}')
