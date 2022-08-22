import platform
from pathlib import Path

import psutil

from assets.client_status import ClientStatus
from assets.constants import APP_NAME, VERSION_STR
from module.singleton_type import SingletonType
from module.utils import (get_script_memory_usage, get_script_uptime,
                          get_system_description, get_system_memory_usage,
                          get_system_uptime)


class Global(metaclass=SingletonType):
    """全局变量，单例模式"""

    ############
    # 全局的变量 #
    ############

    exit_code = 0  # 退出码
    time_to_exit = False  # 是时候退出了
    debug_mode = False  # 调试模式
    test_mode = False  # 测试模式，加载测试插件

    websocket_message_count = 0  # WebSocket 消息计数

    ############
    # 共享的对象 #
    ############

    user_config = None  # 用户配置  # type: UserConfig
    database = None  # 数据库  # type: Database
    command_handler = None  # 命令处理器  # type: CommandHandler
    kenko_go = None  # 应用程序  # type: KenkoGo
    plugin_manager = None  # 插件管理器  # type: PluginManager

    args_known = ()  # 命令行参数
    args_unknown = ()  # 未知命令

    ############
    # 目录与路径 #
    ############

    root_dir = Path('.')  # 根目录
    asset_dir = Path(root_dir, 'assets')  # 静态资源目录
    download_dir = Path(root_dir, 'downloads')  # 下载目录

    def __init__(self):
        # 创建目录
        for dir_ in [self.asset_dir, self.download_dir]:
            dir_.mkdir(parents=True, exist_ok=True)

    @property
    def information(self) -> ClientStatus:
        """获取应用信息"""
        return ClientStatus(
            python_version=platform.python_version(),
            system_description=get_system_description(),

            system_cpu_present=psutil.cpu_percent(),
            system_memory_usage=get_system_memory_usage(),
            kenkogo_memory_usage=get_script_memory_usage(),

            system_uptime=get_system_uptime(),
            kenkogo_uptime=get_script_uptime(),

            connected=self.kenko_go.websocket_connected,
            app_name=APP_NAME,
            version=VERSION_STR,
            websocket_message_count=self.websocket_message_count,
        )


if __name__ == '__main__':
    print(Global().debug_mode)
