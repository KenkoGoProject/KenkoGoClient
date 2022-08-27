from assets.simple_plugin import SimplePlugin


class GoodBye(SimplePlugin):
    """你甚至可以在继承SimplePlugin的情况下只保留一些属性"""

    PLUGIN_NAME = '再见，世界！'  # 插件名称
    PLUGIN_DESCRIPTION = '插件也可以是一个包'  # 插件描述
    PLUGIN_VERSION = '1.2.3'  # 插件版本
