import argparse
import signal
import sys
from typing import Any, Type

from rich.traceback import install as install_rich_traceback

from assets.constants import APP_DESCRIPTION, APP_NAME, VERSION_STR
from module.command_handler import CommandHandler
from module.global_dict import Global
from module.logger_ex import LoggerEx, LogLevel
from module.user_config import UserConfig
from module.utils import change_console_title


def signal_handler(sign: int, _) -> None:
    """信号处理器"""
    if sign in (signal.SIGINT, signal.SIGTERM):
        log.debug(f'Received signal {sign}, Application exits.')
        Global().time_to_exit = True  # 收到退出信号，标记退出
        raise KeyboardInterrupt  # 抛出异常，在Linux下让主线程退出


if __name__ == '__main__':
    install_rich_traceback(console=None, show_locals=True)  # 捕获未处理的异常
    change_console_title(f'{APP_NAME} {VERSION_STR}')  # 修改控制台窗口标题

    # 让PyCharm调试输出的信息换行
    if sys.gettrace() is not None:
        print('Debug Mode')
        Global().debug_mode = True

    # 命令行参数解析
    parser = argparse.ArgumentParser(
        description=f'{APP_NAME} - {APP_DESCRIPTION}',  # 应用程序的描述
        add_help=False,  # 不输出自动生成的说明
        exit_on_error=False,  # 发生错误时不退出
    )
    parser.add_argument('-h', '--help', action='store_true', help='Show this message and exit.')
    parser.add_argument('-d', '--debug', action='store_true', help='Debug mode, show debug log.')
    parser.add_argument('-t', '--test', action='store_true', help='Test mode, load test plugin.')
    parser.add_argument('-c', '--config', help='Path of config file.', default='config.yaml')
    args_known, Global().args_unknown = parser.parse_known_args()
    Global().args_known = args_known

    # 如果用户输入了 -h 或 --help，则显示帮助信息并退出
    if args_known.help:
        parser.print_help()
        sys.exit(0)

    Global().debug_mode = args_known.debug or Global().debug_mode  # 开启调试模式
    Global().test_mode = args_known.test or Global().test_mode  # 开启测试模式

    # 创建日志打印器
    log = LoggerEx('Main')
    log.set_level(LogLevel.DEBUG if Global().debug_mode else LogLevel.INFO)

    # 加载用户配置
    try:
        Global().user_config = UserConfig(args_known.config)
    except Exception as e:
        log.exception(e)
        Global().time_to_exit = True
        log.critical('配置文件读取错误！请检查配置文件格式是否正确。')
        sys.exit(-1)

    # 设置信号响应
    signal.signal(signal.SIGINT, signal_handler)
    signal.signal(signal.SIGTERM, signal_handler)

    command_handler = CommandHandler()  # 创建命令处理器
    Global().command_handler = command_handler

    app: Any = None  # 应用程序对象
    type_of_app: Type[Any] = type(app)  # 应用程序类型

    if not Global().time_to_exit:
        try:
            log.debug(f'{APP_NAME} Starting...')
            # 启动应用
            from kenko_go import KenkoGo
            type_of_app = KenkoGo
            app = KenkoGo()
            Global().kenko_go = app
            app.start()
        except Exception as e:
            log.exception(e)
            Global().time_to_exit = True
            log.critical('Critical Error, Application exits abnormally.')  # 发生致命错误，应用异常退出

    while not Global().time_to_exit:
        try:
            command: str = log.input('> ')  # 获取用户输入
            command = command.strip()
        except (UnicodeDecodeError, EOFError, KeyboardInterrupt):
            if Global().time_to_exit:
                break  # 退出
            else:
                log.error('Invalid Command')  # 输入的命令无效
        else:
            if command:
                command_handler.add(command)

    if isinstance(app, type_of_app):
        app.stop()  # noqa

    log.debug(f'{APP_NAME} exits.')
    sys.exit(Global().exit_code)
