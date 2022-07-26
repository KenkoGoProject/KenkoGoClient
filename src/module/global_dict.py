from pathlib import Path
from typing import Any

from module.console import Console
from module.singleton_type import SingletonType


class Global(metaclass=SingletonType):
    """单例模式，全局变量"""
    _members: dict[str, Any] = {}
    __dict__ = _members

    app_name = 'KenkoGoClient'  # 应用名称
    author_name = 'AkagiYui'  # 作者
    version_num = 1  # 版本号
    version_str = '0.1.0'  # 版本名称
    description = 'A simple client of KenkoGoServer'  # 描述

    exit_code = 0  # 退出码
    time_to_exit = False  # 是时候退出了

    debug_mode = False  # 调试模式
    command: str = ''  # 命令
    user_config = None  # 用户配置  # type: UserConfig
    console: Console = None  # 控制台对象

    args_known = ()  # 命令行参数
    args_unknown = ()  # 未知命令

    #######
    # 路径 #
    #######

    root_dir = Path('.')  # 根目录
    asset_dir = Path(root_dir, 'assets')  # 静态资源目录
    download_dir = Path(asset_dir, 'downloads')  # 下载目录

    # def __setattr__(self, key, value):
    #     self._members[key] = value
    #
    # def __getattr__(self, key):
    #     try:
    #         return self._members[key]
    #     except KeyError:
    #         return None
    #
    # def __delattr__(self, key):
    #     del self._members[key]

    def __repr__(self):
        return self._members.__repr__()

    def __getitem__(self, item):
        return self._members[item]

    def __setitem__(self, key, value):
        self._members[key] = value

    def __delitem__(self, key):
        del self._members[key]

    def __iter__(self):
        return iter(self._members)

    def items(self):
        return self._members.items()

    def keys(self):
        return self._members.keys()

    def values(self):
        return self._members.values()

    def clear(self):
        self._members.clear()


if __name__ == '__main__':
    for k, v in Global().items():
        print(k, v)

    Global().debug_mode = True
    print(Global().debug_mode)
