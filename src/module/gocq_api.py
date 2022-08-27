import traceback
from typing import Optional

import requests

from assets.api_result.send_msg_result import SendMsgResult
from assets.api_result.stranger_info import StrangerInfo
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
        j = response.json()
        if j['retcode'] == 0:
            d = j['data']
            return SendMsgResult(d['message_id'])
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

    def set_friend_add_request(self, flag: str, approve=True, remark: str = None) -> dict:
        """同意/拒绝好友请求

        :param flag: 好友请求标识
        :param approve: 是否同意
        :param remark: 备注，可选
        :return: go-cqhttp API 返回值
        """
        d = {
            'flag': flag,
            'remark': remark,
            'approve': approve
        }
        self.log.info(f'[set_friend_add_request] {flag} {remark} {approve}')
        response = self.r.post(f'{self.base_url}/set_friend_add_request', json=d)  # type: ignore[attr-defined]
        return response.json()

    def get_login_info(self) -> dict:
        """获取登录号信息

        :return: go-cqhttp API 返回值
        """
        self.log.info('[get_login_info]')
        response = self.r.get(f'{self.base_url}/get_login_info')
        return response.json()

    def get_group_info(self, group_id: int, no_cache=False) -> dict:
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
        return response.json()

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
        j = response.json()
        if j['retcode'] == 0:
            d = j['data']
            return StrangerInfo(
                user_id=d['user_id'],
                nickname=d['nickname'],
                sex=d['sex'],
                age=d['age'],
                qid=d['qid'],
                level=d['level'],
                login_days=d['login_days']
            )
        return None

    def get_nickname(self, user_id: int) -> Optional[str]:
        """获取 QQ 号的昵称

        :param user_id: 目标 QQ 账号
        :return: QQ 昵称 """
        if r := self.get_stranger_info(user_id):
            return r.nickname
        return None

    def get_msg(self, message_id: int) -> dict:
        """获取消息

        :param message_id: 消息 ID
        :return: go-cqhttp API 返回值 """
        self.log.info(f'[get_msg] {message_id}')
        d = {
            'message_id': message_id
        }
        response = self.r.post(f'{self.base_url}/get_msg', json=d)
        return response.json()
