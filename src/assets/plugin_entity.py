from typing import Optional

from assets.simple_plugin import SimplePlugin


class Plugin:
    """插件类"""

    def __init__(self, module_name: str):
        self.module_name = module_name  # 插件模块名
        self.module = None  # 插件模块
        self.should_enable = False  # 插件是否应该启用

        self.class_name = ''  # 插件类名
        self.name = ''  # 插件名
        self.description = ''  # 插件描述
        self.description_long = ''  # 长描述，用于插件详情页
        self.author = ''  # 插件作者
        self.help_text = ''  # 插件帮助文本
        self.link = ''  # 插件链接
        self.version = ''  # 插件版本

        self.obj: Optional[SimplePlugin] = None  # 插件对象
        self.loaded = False  # 插件是否加载
        self.initialized = False  # 插件是否初始化
        self.enable = False  # 插件是否启用

    def to_dict(self) -> dict:
        """转换为字典"""
        return {
            'module_name': self.module_name,
            'should_enable': self.enable,
        }

    def load_info(self) -> None:
        """加载插件信息"""
        self.name = self.obj.name
        self.description = self.obj.description
        self.version = self.obj.version
