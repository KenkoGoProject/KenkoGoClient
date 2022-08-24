from assets.cq_code import CqCode
from assets.simple_plugin import SimplePlugin


class HelloWorld(SimplePlugin):
    """你可以继承 SimplePlugin 以省略一些方法"""
    def __init__(self, *args, **kwargs):
        """实例初始化

        插件初始化，你可以在这里初始化一些依赖
        """
        super().__init__(*args, **kwargs)
        self.name = '你好，世界！'  # 插件名称
        self.description = '这是一个插件示例'  # 插件描述
        self.version = '1.0.0'  # 插件版本

        self.description_long = ''  # 长描述，用于插件详情页
        self.author = ''  # 插件作者
        self.help_text = ''  # 插件帮助文本
        self.link = ''  # 插件链接

    def on_enable(self):
        """插件被启用"""
        print('HelloWorld enabled')
        return self  # 务必返回self

    def on_before_disable(self):
        """插件将被禁用，你还可以处理一些事情"""
        print('HelloWorld will be disabled')
        return self  # 务必返回self

    def on_disable(self):
        """插件已被禁用，可以用于清理一些资源"""
        print('HelloWorld disabled')
        return self  # 务必返回self

    def on_connect(self):
        """已连接到KenkoGo服务器"""
        print('server connected')
        return self  # 务必返回self

    def on_disconnect(self):
        """已断开服务器连接"""
        print('server disconnected')
        return self  # 务必返回self

    def on_message(self, message: dict) -> bool:
        """收到 go-cqhttp 消息

        遵循 go-cqhttp 版的 OneBot 消息格式
        """
        if message['post_type'] == 'message':
            msg: str = message['raw_message']
            if CqCode.at(message['self_id']) in msg:
                print('有人叫我')
                message['message'] = '我希望你把篮球和鸡联系起来想想'
                self.api.send_msg(message)
        return True  # 返回True表示消息将被传递给下一个插件，返回False表示消息被拦截
