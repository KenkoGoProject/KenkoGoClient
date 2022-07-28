import traceback
from pathlib import Path
from typing import Dict, Optional

import requests

from module.global_dict import Global
from module.logger_ex import LoggerEx, LogLevel


class ServerApi:
    """ KenkoGoServer 接口"""
    def __init__(self, host_and_port: str, name=None):
        """初始化

        :param host_and_port: 地址和端口，如：127.0.0.1:18082
        :param name: 调用者名称
        """
        self.name = name or traceback.extract_stack()[-2].name
        self.log = LoggerEx(f'{self.__class__.__name__} {name}')
        if Global().debug_mode:
            self.log.set_level(LogLevel.DEBUG)

        self.base_url = f'http://{host_and_port}'  # 基础url
        self.r = requests.Session()  # 初始化 requests 对象

    def stop_instance(self) -> bool:
        """停止实例

        可能导致无法在 QQ 控制，请谨慎使用

        :return: 是否成功
        """
        self.log.debug('Stopping instance...')
        url = f'{self.base_url}/instance/stop'
        try:
            result = self.r.post(url).json()
        except Exception as e:
            self.log.error(f'Instance stop failed: {e}')
            return False
        if result['code'] == 200:
            self.log.debug('Instance stopped.')
            return True
        self.log.error(f'Instance stop failed: {result["msg"]}')
        return False

    def start_instance(self) -> bool:
        """启动实例

        :return: 是否成功
        """
        self.log.debug('Starting instance...')
        url = f'{self.base_url}/instance/start'
        try:
            result = self.r.post(url).json()
        except Exception as e:
            self.log.error(f'Instance start failed: {e}')
            return False
        if result['code'] == 200:
            self.log.debug('Instance started.')
            return True
        self.log.error(f'Instance start failed: {result["msg"]}')
        return False

    def get_qrcode(self) -> Optional[bytes]:
        """获取登录二维码

        :return: 二维码图片，None 表示获取失败或没有二维码
        """
        self.log.debug('Getting qrcode...')
        url = f'{self.base_url}/instance/qrcode'
        try:
            result = self.r.get(url)
        except Exception as e:
            self.log.error(f'Getting qrcode failed: {e}')
            return None
        if result.headers['Content-Type'] != 'image/png':
            self.log.error('Invalid Content-Type.')
            return None
        result = result.content
        self.log.debug('Qrcode got.')
        return result

    def get_status(self) -> Optional[dict]:
        """获取服务器状态

        :return: 服务器状态，None 表示获取失败
        """
        url = f'{self.base_url}/info'
        try:
            result = self.r.get(url).json()
        except Exception as e:
            self.log.error(f'Getting status failed: {e}')
            return None
        if result['code'] == 200:
            return result['data']
        self.log.error(f'Getting status failed: {result["msg"]}')
        return None

    def upload_file(self, file: str) -> Optional[Dict[str, str]]:
        """上传文件

        :param file: 文件路径
        :return: 文件信息，None 表示上传失败
        """
        self.log.debug('Uploading file...')
        url = f'{self.base_url}/client/upload'
        files = [
            ('file', (Path(file).name, open(file, 'rb')))
        ]
        try:
            result = self.r.post(url, files=files).json()
        except Exception as e:
            self.log.error(f'Uploading file failed: {e}')
            return None
        if result['code'] == 200:
            self.log.debug(f'File uploaded. {result["data"]}')
            return result['data']
        self.log.error(f'File upload failed: {result["msg"]}')
        return None


if __name__ == '__main__':
    api = ServerApi('127.0.0.1:18082')
    print(api.upload_file(r'G:\【音频】\安静纯音\Foxtail-Grass Studio - 靴下をはいた猫.mp3'))
