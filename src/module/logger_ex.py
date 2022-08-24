import logging
import traceback
from logging import Formatter
from typing import Union

import rich
from rich.console import ConsoleRenderable
from rich.logging import RichHandler
from rich.pretty import pprint


class LogLevel(int):
    CRITICAL = logging.CRITICAL  # 50
    FATAL = CRITICAL
    ERROR = logging.ERROR  # 40
    WARNING = logging.WARNING  # 30
    INFO = logging.INFO  # 20
    DEBUG = logging.DEBUG  # 10
    TRACE = 5
    NOTSET = logging.NOTSET  # 0


def patch_root_logger() -> None:
    """修改 root logger 的基础配置"""
    rich_handler = RichHandler(show_time=False, show_path=False, rich_tracebacks=True, tracebacks_show_locals=True)
    fmt_string = '%(asctime)s.%(msecs)03d %(message)s'
    rich_handler.setFormatter(Formatter(fmt=fmt_string, datefmt='%Y-%m-%d %H:%M:%S'))
    logging.basicConfig(handlers=[rich_handler])


class LoggerEx:
    """增强 Logger """
    def __init__(self, name: str = None, log_level: int = LogLevel.INFO, show_name: bool = True):
        """初始化

        :param name: logger name
        :param log_level: logger level
        :param show_name: 是否显示 logger name
        """
        self.name = name or traceback.extract_stack()[-2].name
        self.show_name = show_name
        self.logger = logging.getLogger(self.name)

        if not self.logger.hasHandlers():
            rich_handler = RichHandler(show_time=False,
                                       show_path=False,
                                       rich_tracebacks=True,
                                       tracebacks_show_locals=True)
            fmt_string = '%(asctime)s.%(msecs)03d '
            if show_name:
                fmt_string += f'[{self.name}] '
            fmt_string += '%(message)s'
            rich_handler.setFormatter(Formatter(fmt=fmt_string, datefmt='%Y-%m-%d %H:%M:%S'))
            self.console = rich_handler.console
            self.logger.addHandler(rich_handler)
        self.logger.setLevel(log_level)

    def set_level(self, level: int) -> None:
        """设置 logger 的 level

        :param level: logger level"""

        self.logger.setLevel(level)

    def print(self, *obj: Union[ConsoleRenderable, str], **kwargs) -> None:
        """打印对象"""
        if hasattr(self, 'console'):
            self.console.print(*obj)
        else:
            rich.print(*obj, **kwargs)

    @staticmethod
    def print_object(_object) -> None:
        """打印对象

        :param _object: 欲打印对象"""
        pprint(_object, expand_all=True)

    def input(self, *args, **kwargs) -> str:
        """打印 input"""
        if hasattr(self, 'console'):
            return self.console.input(*args, **kwargs)
        else:
            return input(*args, **kwargs)

    def debug(self, *args, **kwargs) -> None:
        """输出 debug 等级的日志"""
        self.logger.debug(*args, **kwargs)

    def info(self, *args, **kwargs) -> None:
        """输出 info 等级的日志"""
        self.logger.info(*args, **kwargs)

    def warning(self, *args, **kwargs) -> None:
        """输出 warning 等级的日志"""
        self.logger.warning(*args, **kwargs)

    def error(self, *args, **kwargs) -> None:
        """输出 error 等级的日志"""
        self.logger.error(*args, **kwargs)

    def critical(self, *args, **kwargs) -> None:
        """输出 critical 等级的日志"""
        self.logger.critical(*args, **kwargs)

    def exception(self, *args, **kwargs) -> None:
        """打印 exception"""
        self.logger.exception(*args, **kwargs)


if __name__ == '__main__':

    def haha():
        log = LoggerEx(log_level=LogLevel.DEBUG)
        log.info("Hello, World!")
        log.critical("[blue underline]Hello, World!")
        log.debug("[blue underline]Hello, World!")
        log.warning("Hello, World!")
        log.error("Hello, World!")
        # log.trace("Hello, World!")

    log = LoggerEx('abc')
    log.info(233)

    log = LoggerEx('abc')
    log.info(456)
