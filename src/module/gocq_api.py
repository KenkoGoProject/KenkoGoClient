import traceback

import requests

from module.global_dict import Global
from module.logger_ex import LoggerEx, LogLevel


class GocqApi:
    """go-cqhttp 原生 API"""

    def __init__(self, host_and_port: str, name: str):
        """初始化

        :param host_and_port: 地址和端口，如：127.0.0.1:18082
        :param name: 调用者名称
        """
        self.name = name or traceback.extract_stack()[-2].name
        self.log = LoggerEx(f'{self.__class__.__name__} {name}')
        if Global().debug_mode:
            self.log.set_level(LogLevel.DEBUG)

        self.base_url = f'http://{host_and_port}/client/api'  # 基础url
        self.r = requests.Session()  # 初始化 requests 对象
        self.r.headers.update({'Content-Type': 'application/json'})

    def send_private_msg(self, user_id: int, message: str, auto_escape: bool = False, from_group: int = None) -> dict:
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
        self.log.info(f'[send_private_msg] {user_id}: {message}')
        response = self.r.post(f'{self.base_url}/send_private_msg', json=j)  # type: ignore[attr-defined]
        return response.json()

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
        self.log.info(f'[send_group_msg] {group_id}: {message}')
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
            self.log.info(f'[send_msg] Group({message["group_id"]}): {message["message"]}')
        elif 'user_id' in message:
            self.log.info(f'[send_msg] User({message["user_id"]}): {message["message"]}')
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
