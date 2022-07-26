from module.global_dict import Global
from module.logger_ex import LogLevel, LoggerEx


class ServerApi:
    def __init__(self):
        self.log = LoggerEx(self.__class__.__name__)
        if Global().debug_mode:
            self.log.set_level(LogLevel.DEBUG)

