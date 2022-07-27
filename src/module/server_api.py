import traceback
from typing import Optional, Union

import requests

from module.global_dict import Global
from module.logger_ex import LoggerEx, LogLevel


class ServerApi:
    def __init__(self, name=None):
        self.name = name or traceback.extract_stack()[-2].name
        self.log = LoggerEx(f'{self.__class__.__name__} {name}')
        if Global().debug_mode:
            self.log.set_level(LogLevel.DEBUG)

        user_config = Global().user_config
        self.base_url = f'http://{user_config.host}:{user_config.port}'
        self.r = requests.Session()
        self.r.headers.update({'Content-Type': 'application/json'})

    def stop_instance(self) -> bool:
        """停止实例，可能导致无法在 QQ 控制，请谨慎使用。"""
        self.log.debug('Stopping instance...')
        url = f'{self.base_url}/instance/stop'
        result = self.r.post(url).json()
        if result['code'] == 200:
            self.log.debug('Instance stopped.')
            return True
        self.log.error(f'Instance stop failed: {result["msg"]}')
        return False

    def start_instance(self) -> bool:
        """启动实例"""
        self.log.debug('Starting instance...')
        url = f'{self.base_url}/instance/start'
        result = self.r.post(url).json()
        if result['code'] == 200:
            self.log.debug('Instance started.')
            return True
        self.log.error(f'Instance start failed: {result["msg"]}')
        return False

    def get_qrcode(self) -> Optional[bytes]:
        """获取登录二维码"""
        self.log.debug('Getting qrcode...')
        url = f'{self.base_url}/instance/qrcode'
        result = self.r.get(url)
        if result.headers['Content-Type'] != 'image/png':
            self.log.error('Invalid Content-Type.')
            return None
        result = result.content
        self.log.debug('Qrcode got.')
        return result

    def get_status(self) -> Union[dict, str]:
        """获取服务器状态"""
        url = f'{self.base_url}/info'
        result = self.r.get(url).json()
        if result['code'] == 200:
            return result['data']
        return result['msg']
