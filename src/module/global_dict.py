from pathlib import Path

from module.singleton_type import SingletonType


class Global(metaclass=SingletonType):
    """单例模式，全局变量"""

    ############
    # 基础的信息 #
    ############

    app_name = 'KenkoGoClient'  # 应用名称
    author_name = 'AkagiYui'  # 作者
    version_num = 6  # 版本号
    version_str = '0.2.0'  # 版本名称
    description = 'A simple client of KenkoGoServer'  # 描述

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
    console = None  # 控制台对象  # type: Console
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


if __name__ == '__main__':
    print(Global().debug_mode)
