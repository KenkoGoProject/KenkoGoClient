from assets.cq_code import CqCode
from module.client_api import ClientApi
from module.global_dict import Global
from module.gocq_api import GocqApi
from module.logger_ex import LoggerEx, LogLevel
from module.message_config import MessageConfig
from module.server_api import ServerApi
from module.singleton_type import SingletonType

ADMIN_HELP_TEXT = f"""管理员操作菜单：
当前版本({Global().version_str})支持的命令：
!h - 显示本信息
!help - 显示帮助信息（非管理员特有）
!status - 显示当前状态
!screen - 截屏
!add - 将本群加入白名单
!del - 将本群从白名单移除"""

HELP_TEXT = """操作菜单：
"""


class MessageManager(metaclass=SingletonType):
    """消息管理器，用于处理 go-cqhttp 消息"""

    def __init__(self):
        """初始化"""

        self.log = LoggerEx(self.__class__.__name__)
        if Global().debug_mode:
            self.log.set_level(LogLevel.DEBUG)

        self.enable = False

        user_config = Global().user_config
        host_and_port = f'{user_config.host}:{user_config.port}'
        token = user_config.token

        self.api = GocqApi(host_and_port, token, self.__class__.__name__)
        self.client = ClientApi(self.__class__.__name__)
        self.server = ServerApi(host_and_port, token, self.__class__.__name__)

        self.config: MessageConfig = user_config.message_config
        self.log.print_object(self.config.to_dict())

    def on_initialize(self):
        """插件初始化"""
        self.log.debug('MessageManager initialized')
        return self

    def on_enable(self):
        """插件被启用"""
        self.enable = True
        self.log.debug('MessageManager enabled')
        return self

    def on_connect(self):
        """已连接到KenkoGo服务器"""
        ...
        return self

    def on_disconnect(self):
        """已断开服务器连接"""
        ...
        return self

    def on_message(self, message: dict):
        """收到 go-cqhttp 消息"""
        if not self.enable:
            return self
        post_type = message['post_type']
        if post_type == 'message':
            return self.type_message(message)
        elif post_type == 'notice':
            return self.type_notice(message)
        return True

    def type_notice(self, message: dict) -> bool:
        """收到 go-cqhttp 通知"""
        notice_type = message['notice_type']
        user_id = message['user_id']

        # 是否屏蔽自己的消息
        if self.config.block_self and user_id == message['self_id']:
            return False

        if notice_type == 'poke':    # 戳一戳
            ...

        return True

    def type_message(self, message: dict) -> bool:
        """收到 go-cqhttp 消息"""
        msg = message['message'].strip()
        user_id = message['user_id']
        message_type = message['message_type']

        # 是否屏蔽自己的消息
        if self.config.block_self and user_id == message['self_id']:
            return False

        if user_id in self.config.administrators:
            if msg == '!h':  # 发送管理员操作菜单
                message['message'] = ADMIN_HELP_TEXT
                self.api.send_msg(message)
                return False
            elif msg == '!screen':  # 发送屏幕截图
                message['message'] = CqCode.image(get_screenshot())
                self.api.send_msg(message)
                return False
            elif msg == '!status':  # 发送服务器信息
                message['message'] = self.get_status()
                self.api.send_msg(message)
                return False
            elif message_type == 'group':
                if msg == '!?' :  # 判断群是否在白名单中
                    group_id = message['group_id']
                    group_info = self.api.get_group_info(group_id)['data']
                    group_name = group_info['group_name']
                    if group_id in self.config.whitelist_groups:
                        msg = f'群 {group_name}({group_id}) 在白名单中'
                    else:
                        msg = f'群 {group_name}({group_id}) 不在白名单中'
                    message['message'] = msg
                    self.api.send_msg(message)
                    return False
                elif msg == '!add':  # 将群加入白名单
                    group_id = message['group_id']
                    group_info = self.api.get_group_info(group_id)['data']
                    group_name = group_info['group_name']
                    if group_id in self.config.whitelist_groups:
                        msg = f'群 {group_name}({group_id}) 已在白名单中'
                    else:
                        self.config.whitelist_groups.add(group_id)
                        self.config.save()
                        msg = f'群 {group_name}({group_id}) 已加入白名单'
                    message['message'] = msg
                    self.api.send_msg(message)
                    return False
                elif msg == '!del':  # 将群从白名单移除
                    group_id = message['group_id']
                    group_info = self.api.get_group_info(group_id)['data']
                    group_name = group_info['group_name']
                    if group_id not in self.config.whitelist_groups:
                        msg = f'群 {group_name}({group_id}) 不在白名单中'
                    else:
                        self.config.whitelist_groups.discard(group_id)
                        self.config.save()
                        msg = f'群 {group_name}({group_id}) 已从白名单移除'
                    message['message'] = msg
                    self.api.send_msg(message)
                    return False

        # 放行管理员消息
        if user_id not in self.config.administrators:
            # 屏蔽黑名单用户
            if user_id in self.config.block_users:
                self.log.debug(f'Message from blocked account {user_id}')
                return False

            if message_type == 'private':  # 私聊消息
                if self.config.block_private:
                    return False  # 屏蔽私聊消息
                if self.config.whitelist_mode and user_id not in self.config.whitelist_users:
                    return False  # 屏蔽非白名单用户
            if message_type == 'group':  # 群聊消息
                if self.config.block_group:
                    return False  # 屏蔽群聊消息
                group_id = message['group_id']
                if self.config.whitelist_mode and group_id not in self.config.whitelist_groups:
                    return False  # 屏蔽非白名单群聊
                if group_id in self.config.block_groups:
                    return False  # 屏蔽黑名单群聊

        if msg == '!help':
            message['message'] = HELP_TEXT
            self.api.send_msg(message)
            return False
        return True

    def get_status(self) -> str:
        """获取服务器状态"""
        status = self.server.get_status()
        import json
        result = json.dumps(status, ensure_ascii=False, indent=4)
        status = self.client.get_info()
        result += '\n' + json.dumps(status, ensure_ascii=False, indent=4)
        return result


def get_screenshot() -> bytes:
    """截屏"""
    from io import BytesIO

    from PIL import ImageGrab
    with BytesIO() as f:
        ImageGrab.grab(all_screens=True).save(f, 'PNG')
        f.seek(0)
        return f.read()
