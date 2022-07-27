import traceback

import requests

from module.global_dict import Global
from module.logger_ex import LoggerEx, LogLevel


class GocqApi:
    def __init__(self, name: str):
        self.name = name or traceback.extract_stack()[-2].name
        self.log = LoggerEx(f'{self.__class__.__name__} {name}')
        if Global().debug_mode:
            self.log.set_level(LogLevel.DEBUG)

        user_config = Global().user_config
        self.base_url = f'http://{user_config.host}:{user_config.port}/client/api'
        self.r: requests = requests.Session()  # type: ignore[valid-type]
        self.r.headers.update({'Content-Type': 'application/json'})

    def send_private_msg(self, user_id: int, message: str, auto_escape: bool = False, from_group: int = None):
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

    def send_group_msg(self, group_id: int, message: str, auto_escape: bool = False):
        d = {
            'group_id': group_id,
            'message': message,
            'auto_escape': auto_escape
        }
        self.log.info(f'[send_group_msg] {group_id}: {message}')
        response = self.r.post(f'{self.base_url}/send_group_msg', json=d)  # type: ignore[attr-defined]
        return response.json()

    def send_msg(self, message: dict, auto_escape: bool = False):
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

    def set_friend_add_request(self, flag: str, approve=True, remark: str = None):
        d = {
            'flag': flag,
            'remark': remark,
            'approve': approve
        }
        self.log.info(f'[set_friend_add_request] {flag} {remark} {approve}')
        response = self.r.post(f'{self.base_url}/set_friend_add_request', json=d)  # type: ignore[attr-defined]
        return response.json()

    def get_login_info(self):
        self.log.info('[get_login_info]')
        response = self.r.get(f'{self.base_url}/get_login_info')
        return response.json()
