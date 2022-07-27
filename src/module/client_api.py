from module.global_dict import Global
from module.logger_ex import LoggerEx, LogLevel


class ClientApi:
    """Client API"""

    def __init__(self, name):
        self.log = LoggerEx(f'{self.__class__.__name__} {name}')
        if Global().debug_mode:
            self.log.set_level(LogLevel.DEBUG)

    @staticmethod
    def get_info() -> dict:
        """获取Client的信息"""
        return {
            'app_name': Global().app_name,
            'version': Global().version_str,
        }
