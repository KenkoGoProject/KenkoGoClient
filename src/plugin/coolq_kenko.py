from assets.simple_plugin import SimplePlugin
from module.client_api import ClientApi
from module.gocq_api import GocqApi
from module.server_api import ServerApi


class Coolq(SimplePlugin):

    def __init__(self, api: GocqApi, client: ClientApi, server: ServerApi):
        super().__init__(api, client, server)
        self.api = api
        self.client = client
        self.server = server
        self.name = '仿CoolQ事件'
        self.description = '还原CoolQ事件的插件'
        self.version = '1.0.0'

    def on_message(self, message: dict):
        if message['post_type'] == 'message':
            if message['message_type'] == 'private':
                return self.on_private_message(message['sub_type'], message['time'], message['user_id'], message['raw_message'], message['font'])
            elif message['message_type'] == 'group':
                return self.on_group_message(message['sub_type'], message['time'], message['group_id'], message['user_id'], message['anonymous'], message['raw_message'], message['font'])
        return True

    def on_private_message(self, sub_type, send_time, from_qq, msg, font) -> bool:
        """当收到私聊消息

        :param sub_type: 消息子类型，friend: 好友, group: 群临时会话, group_self: 群自己发的消息, other: 其他
        :param send_time: 消息发送时间
        :param from_qq: 消息来源QQ
        :param msg: 消息内容
        :param font: 消息字体
        :return: True表示消息将被传递给下一个插件，False表示消息被拦截
        """
        return True

    def on_group_message(self, sub_type, send_time, from_group, from_qq, from_anonymous, msg, font) -> bool:
        """当收到群聊消息

        :param sub_type: 消息子类型，normal: 普通消息, notice: 系统通知, anonymous: 匿名消息,
        :param send_time: 消息发送时间
        :param from_group: 消息来源群
        :param from_qq: 消息来源QQ
        :param from_anonymous: 消息来源匿名者
        :param msg: 消息内容
        :param font: 消息字体
        :return: True表示消息将被传递给下一个插件，False表示消息被拦截
        """
        return True
