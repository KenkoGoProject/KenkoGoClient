from assets.cq_code import CqCode
from assets.simple_plugin import SimplePlugin


class HelloWorld(SimplePlugin):
    """这是一个插件示例"""

    PLUGIN_NAME = '你好，世界！'  # 插件名称
    PLUGIN_DESCRIPTION = '这是一个插件示例'  # 插件描述
    PLUGIN_VERSION = '1.0.0'  # 插件版本
    # 你需要至少设置以上三个类属性

    PLUGIN_DESCRIPTION_LONG = PLUGIN_DESCRIPTION  # 长描述，用于插件详情页
    PLUGIN_AUTHOR = 'AkagiYui'  # 插件作者
    PLUGIN_HELP_TEXT = '当有人@机器人时，机器人会让你想想'  # 插件帮助文本
    PLUGIN_LINK = 'https://akagiyui.com'  # 插件链接

    def __init__(self, *args, **kwargs):
        """实例初始化

        插件初始化，你可以在这里初始化一些依赖
        """
        super().__init__(*args, **kwargs)

    def on_enable(self):
        """插件被启用"""
        self.logger.info('HelloWorld enabled')
        return self  # 务必返回self

    def on_before_disable(self):
        """插件将被禁用，你还可以处理一些事情"""
        self.logger.info('HelloWorld will be disabled')
        return self  # 务必返回self

    def on_disable(self):
        """插件已被禁用，可以用于清理一些资源"""
        self.logger.info('HelloWorld disabled')
        return self  # 务必返回self

    def on_connect(self):
        """已连接到KenkoGo服务器"""
        self.logger.info('server connected')
        return self  # 务必返回self

    def on_disconnect(self):
        """已断开服务器连接"""
        self.logger.info('server disconnected')
        return self  # 务必返回self

    def on_message(self, message: dict) -> bool:
        """收到 go-cqhttp 消息

        遵循 go-cqhttp 版的 OneBot 消息格式
        """
        if message['post_type'] == 'message':
            msg: str = message['raw_message']
            if CqCode.at(message['self_id']) in msg:
                self.logger.info('有人叫我')
                message['message'] = '我希望你把篮球和鸡联系起来想想'
                self.api.send_msg(message)
        return True  # 返回True表示消息将被传递给下一个插件，返回False表示消息被拦截
