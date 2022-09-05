import html
import json
import re
import threading
from typing import Generator, List

from assets.constants import ADMIN_HELP_TEXT, HELP_TEXT, INVITE_HELP_TEXT
from assets.cq_code import CqCode
from assets.database_tables.friend_request import FriendRequest
from assets.database_tables.group_invite import GroupInvite
from assets.group_invite_type import GroupInviteType
from module.client_api import ClientApi
from module.global_dict import Global
from module.gocq_api import GocqApi
from module.logger_ex import LoggerEx, LogLevel
from module.message_config import MessageConfig
from module.server_api import ServerApi
from module.singleton_type import SingletonType
from module.utils import get_screenshot


class MessageManager(metaclass=SingletonType):
    """消息管理器，用于处理 go-cqhttp 消息"""

    def __init__(self):
        """初始化"""

        self.log = LoggerEx(self.__class__.__name__)
        if Global().debug_mode:
            self.log.set_level(LogLevel.DEBUG)

        self.is_enable = False

        user_config = Global().user_config
        host_and_port = f'{user_config.host}:{user_config.port}'
        token = user_config.token

        self.api = GocqApi(host_and_port, token, self.__class__.__name__)
        self.client = ClientApi(self.__class__.__name__)
        self.server = ServerApi(host_and_port, token, self.__class__.__name__)

        self.config: MessageConfig = user_config.message_config
        self.command_prefix = self.config.command_prefix

        self.ADMIN_HELP_TEXT = ADMIN_HELP_TEXT.replace('[CP]', self.command_prefix)
        self.HELP_TEXT = HELP_TEXT.replace('[CP]', self.command_prefix)
        self.INVITE_HELP_TEXT = INVITE_HELP_TEXT.replace('[CP]', self.command_prefix)

        self.bot_id: int = -1  # 自身 QQ 号

    def enable(self) -> None:
        """被启用"""
        self.is_enable = True
        self.log.debug('MessageManager enabled')

    def disable(self) -> None:
        """被禁用"""
        self.is_enable = False
        self.log.debug('MessageManager disabled')

    def on_connect(self) -> bool:
        """已连接到KenkoGo服务器"""
        if r := self.api.get_login_info():
            self.bot_id = r.user_id
        return True

    def on_disconnect(self) -> bool:
        """已断开服务器连接"""
        return True

    def on_message(self, message: dict) -> bool:
        """收到 go-cqhttp 消息"""
        if not self.is_enable:
            return True
        post_type = message['post_type']
        if post_type == 'message':
            return self.type_message(message)
        elif post_type == 'notice':
            return self.type_notice(message)
        elif post_type == 'request':
            return self.type_request(message)
        return True

    def type_request(self, message: dict) -> bool:
        """收到 go-cqhttp 请求"""
        request_type = message['request_type']
        if request_type == 'friend':
            self.log.info(f'收到好友请求：{message["user_id"]}({message["comment"]})')
            if not self.config.ignore_friend_request:
                if self.request_friend(message['user_id'], message['flag'], message['comment']):
                    return False
            if self.config.block_friend_request:
                return False
        elif request_type == 'group':
            sub_type = message['sub_type']
            if sub_type == 'invite':
                if self.request_group_invite(message['group_id'], message['flag'], message['user_id']):
                    return False
                if self.config.block_group_invite:
                    return False
        return True

    def request_group_invite(self, group_id: int, flag: str, user_id: int) -> bool:
        """机器人被邀请进群

        :param group_id: 群号
        :param flag: 请求标识
        :param user_id: 邀请者
        :return: 是否已处理
        """
        if stranger_info := self.api.get_stranger_info(user_id):
            stranger_name = f'{stranger_info.nickname}({user_id})'
        else:
            stranger_name = f'{user_id}'
        if group_info := self.api.get_group_info(group_id):
            group_name = f'{group_info.group_name}({group_id})'
        else:
            group_name = f'{group_id}'

        if user_id in self.config.administrators:
            self.api.set_group_add_request(flag, GroupInviteType.INVITE, True)
            self.log.info(f'已同意超级管理员 {stranger_name} 的群聊邀请：{group_name}')
            return True

        def deal_thread():
            if self.api.is_in_group(group_id):
                msg = f'已被 {stranger_name} 邀请进入了群聊：{group_name}。'
            else:
                gi = GroupInvite(
                    group_id=group_id,
                    user_id=user_id,
                    flag=flag
                )
                if not gi.save():
                    self.log.error(f'保存群邀请失败：{gi}')
                msg = f'被 {stranger_name} 邀请进入群聊：{group_name}。'
                msg += self.INVITE_HELP_TEXT.replace('[UUID]', gi.uuid)
            for admin in self.config.administrators:
                self.api.send_private_msg(admin, msg)

        threading.Timer(2.0, deal_thread).start()
        return True

    def request_friend(self, user_id: int, flag: str, comment: str) -> bool:
        """请求加好友

        :param user_id: 好友QQ号
        :param flag: 请求标识
        :param comment: 备注
        :return: 是否已处理
        """
        fr = FriendRequest(
            user_id=user_id,
            comment=comment,
            flag=flag
        )
        if not fr.save():
            self.log.error(f'记录好友请求失败：{fr}')
        if stranger_info := self.api.get_stranger_info(user_id):
            stranger_name = f'{stranger_info.nickname}({user_id})'
        else:
            stranger_name = f'{user_id}'
        msg = f'收到好友请求。\n{stranger_name}：{comment}'
        msg += self.INVITE_HELP_TEXT.replace('[UUID]', fr.uuid)
        for admin in self.config.administrators:
            self.api.send_private_msg(admin, msg)
        return True

    def type_notice(self, message: dict) -> bool:
        """收到 go-cqhttp 通知"""
        notice_type = message['notice_type']
        user_id = message['user_id']

        # 是否屏蔽自己的消息
        if self.config.block_self and user_id == message['self_id']:
            return False

        if notice_type == 'notify':
            sub_type = message['sub_type']
            if sub_type == 'poke':  # 戳一戳
                ...

        return True

    def type_message(self, message: dict) -> bool:
        """收到 go-cqhttp 消息"""
        raw_msg: str = message['raw_message'].strip()
        user_id: int = message['user_id']
        message_type: str = message['message_type']
        command_prefix = self.command_prefix

        # 是否屏蔽自己的消息
        if self.config.block_self and user_id == message['self_id']:
            return False

        # 管理员命令
        if user_id in self.config.administrators:
            if not raw_msg.startswith(command_prefix):
                return True
            msg = raw_msg.removeprefix(command_prefix)
            if msg == 'h':  # 发送管理员操作菜单
                message['message'] = self.ADMIN_HELP_TEXT
                self.api.send_msg(message)
                return False
            elif msg == 'screen':  # 发送屏幕截图
                message['message'] = CqCode.image(get_screenshot())
                self.api.send_msg(message)
                return False
            elif msg == 'status':  # 发送服务器信息
                message['message'] = self.get_status()
                self.api.send_msg(message)
                return False
            elif msg == 'ls':  # 发送白名单/黑名单
                msg = f'白名单用户: {json.dumps(list(self.config.whitelist_users))}'
                msg += '\n白名单群聊: ' + json.dumps(list(self.config.whitelist_groups))
                msg += '\n黑名单用户: ' + json.dumps(list(self.config.block_users))
                msg += '\n黑名单群聊: ' + json.dumps(list(self.config.block_groups))
                message['message'] = msg
                self.api.send_msg(message)
                return False
            elif msg == 'set':  # 发送设置信息
                msg = f'超级管理员: {json.dumps(list(self.config.administrators))}'
                msg += f'\n屏蔽自身消息: {self.config.block_self}'
                msg += f'\n屏蔽私聊消息: {self.config.block_private}'
                msg += f'\n屏蔽群聊消息: {self.config.block_group}'
                msg += f'\n白名单模式（仅响应白名单内成员）: {self.config.whitelist_mode}'
                message['message'] = msg
                self.api.send_msg(message)
                return False
            elif msg == 'todo':  # 发送待办事项
                msg = ''

                frs: List[FriendRequest] = FriendRequest.get_all_not_finish()
                if frs:
                    msg += '好友请求：'
                    for gi in frs:
                        msg += f'\n[{gi.uuid}]{self.api.get_nickname(gi.user_id)}({gi.user_id})：{gi.comment}'

                r: List[GroupInvite] = GroupInvite.get_all_not_finish()
                if r:
                    if msg:
                        msg += '\n'
                    msg += '群聊邀请：'
                    for gi in r:
                        if (group_info := self.api.get_group_info(gi.group_id)) is not None:
                            group_name = f'{group_info.group_name}({gi.group_id})'
                        else:
                            group_name = f'{gi.group_id}'
                        msg += f'\n[{gi.uuid}]{group_name} 来自 {self.api.get_nickname(gi.user_id)}({gi.user_id})'

                if not msg:
                    msg += '暂无待办事项。'
                else:
                    msg += self.INVITE_HELP_TEXT.replace('[UUID]', '[id]')
                message['message'] = msg
                self.api.send_msg(message)
                return False
            elif msg[:2] in {'0 ', '1 ', '2 '}:  # 处理待办事项
                action = msg[0]
                raw_uuid = msg[2:].strip()
                raw_uuid = html.unescape(raw_uuid)
                if not (uuid_groups := re.match(r'\[?(\w+)]?', raw_uuid)):
                    return True
                uuid: str = uuid_groups[1]

                if fr := FriendRequest.get_one_not_finish(uuid):
                    fr.finish(user_id)
                    if action == '1':
                        self.api.set_friend_add_request(fr.flag, True)
                        msg = f'已同意好友请求：{fr.flag}。'
                    elif action == '2':
                        self.api.set_friend_add_request(fr.flag, False)
                        msg = f'已拒绝好友请求：{fr.flag}。'
                    elif action == '0':
                        msg = f'已忽略好友请求：{fr.flag}。'
                elif gi := GroupInvite.get_one_not_finish(uuid):
                    gi.finish(user_id)
                    if action == '1':
                        self.api.set_group_add_request(gi.flag, GroupInviteType.INVITE, True)
                        msg = f'已同意群聊邀请：{gi.flag}。'
                    elif action == '2':
                        self.api.set_group_add_request(gi.flag, GroupInviteType.INVITE, False)
                        msg = f'已拒绝群聊邀请：{gi.flag}。'
                    elif action == '0':
                        msg = f'已忽略群聊邀请：{gi.flag}。'
                else:
                    msg = '未找到该请求！'
                message['message'] = msg
                self.api.send_msg(message)
                return False
            elif message_type == 'group':
                if msg == '?':  # 判断群是否在白名单中
                    group_id = message['group_id']
                    group_name = self.api.get_group_info(group_id).group_name
                    if group_id in self.config.whitelist_groups:
                        msg = f'群 {group_name}({group_id}) 在白名单中'
                    else:
                        msg = f'群 {group_name}({group_id}) 不在白名单中'
                    message['message'] = msg
                    self.api.send_msg(message)
                    return False
                elif msg == 'add':  # 将群加入白名单
                    group_id = message['group_id']
                    group_name = self.api.get_group_info(group_id).group_name
                    if group_id in self.config.whitelist_groups:
                        msg = f'群 {group_name}({group_id}) 已在白名单中'
                    else:
                        self.config.whitelist_groups.add(group_id)
                        self.config.save()
                        msg = f'群 {group_name}({group_id}) 已加入白名单'
                    message['message'] = msg
                    self.api.send_msg(message)
                    return False
                elif msg == 'del':  # 将群从白名单移除
                    group_id = message['group_id']
                    group_name = self.api.get_group_info(group_id).group_name
                    if group_id not in self.config.whitelist_groups:
                        msg = f'群 {group_name}({group_id}) 不在白名单中'
                    else:
                        self.config.whitelist_groups.discard(group_id)
                        self.config.save()
                        msg = f'群 {group_name}({group_id}) 已从白名单移除'
                    message['message'] = msg
                    self.api.send_msg(message)
                    return False

        # 屏蔽各类消息
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
            elif message_type == 'group':  # 群聊消息
                if self.config.block_group:
                    return False  # 屏蔽群聊消息
                group_id = message['group_id']
                if self.config.whitelist_mode and group_id not in self.config.whitelist_groups:
                    return False  # 屏蔽非白名单群聊
                if group_id in self.config.block_groups:
                    return False  # 屏蔽黑名单群聊

        if not raw_msg.startswith(command_prefix):
            return True
        msg = raw_msg.removeprefix(command_prefix)
        if msg in {'help', '?'}:
            message['message'] = self.HELP_TEXT
            self.api.send_msg(message)
            return False
        return True

    # noinspection DuplicatedCode
    def get_status(self) -> str:
        """获取服务器状态"""
        result = '****Server****'
        status = self.server.get_status()
        result += f'\nPython版本：{status.python_version}'
        result += f'\n操作系统：{status.system_description}'
        result += f'\nCPU占用：{status.system_cpu_present}%'
        result += f'\n系统内存占用：{status.system_memory_usage}%'
        result += f'\n脚本内存占用：{status.kenkogo_memory_usage}%'
        result += f'\n系统运行时长：{status.system_uptime}'
        result += f'\n脚本运行时长：{status.kenkogo_uptime}'
        result += f'\n已接收实例消息数：{status.gocq_msg_count}'

        result += '\n****Client****'
        status = self.client.get_info()
        result += f'\nPython版本：{status.python_version}'
        result += f'\n操作系统：{status.system_description}'
        result += f'\nCPU占用：{status.system_cpu_present}%'
        result += f'\n系统内存占用：{status.system_memory_usage}%'
        result += f'\n脚本内存占用：{status.kenkogo_memory_usage}%'
        result += f'\n系统运行时长：{status.system_uptime}'
        result += f'\n脚本运行时长：{status.kenkogo_uptime}'
        result += f'\n脚本版本：{status.version}'
        result += f'\n已接收服务器消息数：{status.websocket_message_count}'
        return result

    def tell_administrators(self, msg: str) -> Generator:
        """向管理员发送消息"""
        for user_id in self.config.administrators:
            yield self.api.send_private_msg(user_id, msg)
