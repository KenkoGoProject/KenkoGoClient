import requests

from module.global_dict import Global


class GocqApi:

    def __init__(self, name: str):
        user_config = Global().user_config
        self.base_url = f'http://{user_config.host}:{user_config.port}/client/api'
        self.r: requests = requests.Session()

    def send_private_msg(self, user_id: int, message: str, auto_escape: bool = False, from_group: int = None):
        j = {
                'user_id': user_id,
                'message': message,
                'auto_escape': auto_escape
        }
        if from_group is not None:
            j['from_group'] = from_group
        response = self.r.post(f'{self.base_url}/send_private_msg', json=j)
        return response.json()

    def send_group_msg(self, group_id: int, message: str, auto_escape: bool = False):
        response = self.r.post(
            f'{self.base_url}/send_group_msg',
            json={
                'group_id': group_id,
                'message': message,
                'auto_escape': auto_escape
            }
        )
        return response.json()

    def send_msg(self, message: dict, auto_escape: bool = False):
        j = {}
        if 'group_id' in message:
            j['group_id'] = message['group_id']
        elif 'user_id' in message:
            j['user_id'] = message['user_id']
        j['message'] = message['message']
        j['auto_escape'] = auto_escape
        response = self.r.post(
            f'{self.base_url}/send_msg',
            json=j
        )
        return response.json()

    def set_friend_add_request(self, flag: str, approve=True, remark: str = None):
        response = self.r.post(
            f'{self.base_url}/set_friend_add_request',
            json={
                'flag': flag,
                'remark': remark,
                'approve': approve
            }
        )
        return response.json()

    def get_login_info(self):
        response = self.r.get(f'{self.base_url}/get_login_info')
        return response.json()
