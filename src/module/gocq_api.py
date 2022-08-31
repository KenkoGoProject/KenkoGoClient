import traceback
from json import JSONDecodeError
from typing import Optional

import requests

from assets.api_result.group_info import GroupInfo
from assets.api_result.login_info import LoginInfo
from assets.api_result.send_msg_result import SendMsgResult
from assets.api_result.stranger_info import StrangerInfo
from assets.group_invite_type import GroupInviteType
from module.global_dict import Global
from module.logger_ex import LoggerEx, LogLevel


class GocqApi:
    """go-cqhttp 原生 API"""

    def __init__(self, host_and_port: str, token: str = None, name: str = None):
        """初始化

        :param host_and_port: 地址和端口，如：127.0.0.1:18082
        :param token: api token
        :param name: 调用者名称
        """
        self.name = name or traceback.extract_stack()[-2].name
        self.log = LoggerEx(f'{self.__class__.__name__} {name}')
        if Global().debug_mode:
            self.log.set_level(LogLevel.DEBUG)

        self.base_url = f'http://{host_and_port}/client/api'  # 基础url
        self.r = requests.Session()  # 初始化 requests 对象
        self.r.headers.update({'Content-Type': 'application/json'})
        if token:
            self.r.headers.update({'Authorization': f'Bearer {token}'})

    def send_private_msg(self, user_id: int, message: str, auto_escape: bool = False, from_group: int = None) \
            -> Optional[SendMsgResult]:
        """发送私聊消息

        :param user_id: 目标 QQ 账号
        :param message: 消息内容
        :param auto_escape: 识别 CQ 码
        :param from_group: 来自群号，可选
        :return: go-cqhttp API 返回值
        """
        j = {
            'user_id': user_id,
            'message': message,
            'auto_escape': auto_escape
        }
        if from_group is not None:
            j['from_group'] = from_group
        self.log.info(f'[send_private_msg] {user_id}: {message[:100]}')
        response = self.r.post(f'{self.base_url}/send_private_msg', json=j)  # type: ignore[attr-defined]
        try:
            j = response.json()['data']
            return SendMsgResult(j['message_id'])
        except (JSONDecodeError, KeyError):
            return None

    def send_group_msg(self, group_id: int, message: str, auto_escape: bool = False) -> dict:
        """发送群聊消息

        :param group_id: 目标群号
        :param message: 消息内容
        :param auto_escape: 识别 CQ 码
        :return: go-cqhttp API 返回值
        """
        d = {
            'group_id': group_id,
            'message': message,
            'auto_escape': auto_escape
        }
        self.log.info(f'[send_group_msg] {group_id}: {message[:100]}')
        response = self.r.post(f'{self.base_url}/send_group_msg', json=d)  # type: ignore[attr-defined]
        return response.json()

    def send_msg(self, message: dict, auto_escape: bool = False) -> dict:
        """发送消息
        根据 group_id 或 user_id 发送消息

        :param message: 消息内容
        :param auto_escape: 识别 CQ 码
        :return: go-cqhttp API 返回值
        """
        d = {}
        if 'group_id' in message:
            d['group_id'] = message['group_id']
        elif 'user_id' in message:
            d['user_id'] = message['user_id']
        else:
            raise ValueError('Invalid message.')
        d['message'] = message['message']
        d['auto_escape'] = auto_escape
        if 'group_id' in message:
            self.log.info(f'[send_msg] Group({message["group_id"]}): {message["message"][:100]}')
        elif 'user_id' in message:
            self.log.info(f'[send_msg] User({message["user_id"]}): {message["message"][:100]}')
        response = self.r.post(f'{self.base_url}/send_msg', json=d)  # type: ignore[attr-defined]
        return response.json()

    def set_friend_add_request(self, flag: str, approve=True, remark: str = None) -> bool:
        """同意/拒绝好友请求

        :param flag: 好友请求标识
        :param approve: 是否同意
        :param remark: 好友备注，可选
        :return: go-cqhttp API 返回值
        """
        d = {
            'flag': flag,
            'remark': remark,
            'approve': approve
        }
        self.log.info(f'[set_friend_add_request] {flag} {remark} {approve}')
        response = self.r.post(f'{self.base_url}/set_friend_add_request', json=d)  # type: ignore[attr-defined]
        j = response.json()
        if j['retcode'] == 0:
            return True
        self.log.error(j)
        return False

    def set_group_add_request(self, flag: str, sub_type: GroupInviteType, approve=True, reason: str = None) -> bool:
        """同意/拒绝群邀请

        :param flag: 好友请求标识
        :param sub_type: 请求类型
        :param approve: 是否同意
        :param reason: 拒绝理由，仅在拒绝时有效
        :return: go-cqhttp API 返回值
        """
        d = {
            'flag': flag,
            'sub_type': sub_type.value,
            'approve': approve
        }
        if (not approve) and reason:
            d['reason'] = reason
        self.log.info(f'[set_group_add_request] {flag} {sub_type} {approve} {reason}')
        response = self.r.post(f'{self.base_url}/set_group_add_request', json=d)
        j = response.json()
        if j['retcode'] == 0:
            return True
        self.log.error(j)
        return False

    def get_login_info(self) -> Optional[LoginInfo]:
        """获取登录号信息

        :return: go-cqhttp API 返回值
        """
        self.log.info('[get_login_info]')
        response = self.r.get(f'{self.base_url}/get_login_info')
        try:
            j = response.json()['data']
            return LoginInfo(j['user_id'], j['nickname'])
        except (JSONDecodeError, KeyError) as e:
            self.log.exception(e)
            return None

    def get_group_info(self, group_id: int, no_cache=False) -> Optional[GroupInfo]:
        """获取群信息

        :param group_id: 群号
        :param no_cache: 是否不使用缓存
        :return: go-cqhttp API 返回值 """
        self.log.info(f'[get_group_info] {group_id}')
        d = {
            'group_id': group_id,
            'no_cache': no_cache
        }
        response = self.r.post(f'{self.base_url}/get_group_info', json=d)
        try:
            j = response.json()['data']
            return GroupInfo(
                group_id=j['group_id'],
                group_name=j['group_name'],
                group_memo=j['group_memo'] if 'group_memo' in j else None,
                group_create_time=j['group_create_time'],
                group_level=j['group_level'],
                member_count=j['member_count'],
                max_member_count=j['max_member_count']
            )
        except (JSONDecodeError, KeyError) as e:
            self.log.exception(e)
            return None

    def get_stranger_info(self, user_id: int, no_cache=False) -> Optional[StrangerInfo]:
        """获取陌生人信息

        :param user_id: 目标 QQ 账号
        :param no_cache: 是否不使用缓存
        :return: go-cqhttp API 返回值 """
        self.log.info(f'[get_stranger_info] {user_id}')
        d = {
            'user_id': user_id,
            'no_cache': no_cache
        }
        response = self.r.post(f'{self.base_url}/get_stranger_info', json=d)
        try:
            j = response.json()['data']
            return StrangerInfo(
                user_id=j['user_id'],
                nickname=j['nickname'],
                sex=j['sex'],
                age=j['age'],
                qid=j['qid'],
                level=j['level'],
                login_days=j['login_days']
            )
        except (JSONDecodeError, KeyError):
            return None

    def get_nickname(self, user_id: int) -> Optional[str]:
        """获取 QQ 号的昵称

        :param user_id: 目标 QQ 账号
        :return: QQ 昵称 """
        if r := self.get_stranger_info(user_id):
            return r.nickname
        return None

    def get_msg(self, message_id: int) -> dict:
        """获取消息，已知通过私聊回复得到的消息id有误

        :param message_id: 消息 ID
        :return: go-cqhttp API 返回值 """
        self.log.info(f'[get_msg] {message_id}')
        d = {
            'message_id': message_id
        }
        response = self.r.post(f'{self.base_url}/get_msg', json=d)
        return response.json()

    def is_in_group(self, group_id: int, user_id: int = None, no_cache=False) -> bool:
        """检查用户是否在群内

        :param group_id: 群号
        :param user_id: 目标 QQ 账号，不填则为登录号
        :param no_cache: 是否不使用缓存
        :return: 是否在群内 """

        self.log.info(f'[is_in_group] {group_id} {user_id if user_id else "self"}')
        if user_id is not None:
            d = {
                'group_id': group_id,
                'user_id': user_id,
                'no_cache': no_cache
            }
            response = self.r.post(f'{self.base_url}/get_group_member_info', json=d)
            j = response.json()
            if j['retcode'] == 0:
                return True
            return False
        else:
            d = {
                'group_id': group_id,
            }
            response = self.r.post(f'{self.base_url}/get_group_member_list', json=d)
            j = response.json()
            if j['retcode'] == 0:
                return True
            return False
