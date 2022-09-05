from typing import Union

from module.utils import base_64


class CqCode:
    """CQ码生成器

    https://docs.go-cqhttp.org/cqcode
    """

    @staticmethod
    def face(face_id: int) -> str:
        """QQ表情 [CQ:face,id=0]
        https://github.com/kyubotics/coolq-http-api/wiki/%E8%A1%A8%E6%83%85-CQ-%E7%A0%81-ID-%E8%A1%A8

        :param face_id: 表情 ID
        :return: CQ 码
        """
        return f'[CQ:face,id={face_id}]'

    @staticmethod
    def image(file, image_type: str = 'normal', use_cache: bool = True, show_id: int = 40000, threads: int = 2) -> str:
        """图片 [CQ:image,file=http://baidu.com/1.jpg,c=2]

        :param file: 图片url 或 bytes(将使用base64编码)
        :param image_type: 图片类型，可选：normal, flash 闪照, show 秀图
        :param use_cache: 使用缓存，只在使用网络 URL 发送时有效
        :param show_id: 秀图特效 id
        :param threads: 下载网络图片并发线程数
        :return: CQ 码
        """
        code = '[CQ:image,file='
        if isinstance(file, str):
            code += f'{file}'
        elif isinstance(file, bytes):
            code += f'base64://{base_64(file)}'
        if image_type == 'flash':
            code += ',type=flash'
        elif image_type == 'show':
            code += ',type=show'
            code += f',id={show_id}'
        if not use_cache:
            code += ',cache=0'
        code += f',c={threads}]'
        return code

    @staticmethod
    def image_local(file_path: str, image_type: str = 'normal',
                    use_cache: bool = True, show_id: int = 40000, threads: int = 2) -> str:
        """图片 [CQ:image,file=1.jpg,c=2]
        使用本地文件

        :param file_path: 图片路径
        :param image_type: 图片类型，可选：normal, flash 闪照, show 秀图
        :param use_cache: 使用缓存，只在使用网络 URL 发送时有效
        :param show_id: 秀图特效 id
        :param threads: 下载网络图片并发线程数
        :return: CQ 码
        """
        # TODO: 先发送文件至服务器
        try:
            with open(file_path, 'rb') as f:
                return CqCode.image(f.read(), image_type, use_cache, show_id, threads)
        except FileExistsError:
            return CqCode.image(f'file:///{file_path}', image_type, use_cache, show_id, threads)

    @staticmethod
    def at(user_id: Union[int, str]) -> str:
        """@消息
        [CQ:at,qq=10001000]

        :param user_id: QQ 号码
        :return: CQ 码
        """
        return f'[CQ:at,qq={user_id}]'

    @staticmethod
    def record(file: Union[str, bytes], use_cache: bool = True) -> str:
        """语音消息
        [CQ:record,file=http://baidu.com/1.mp3]

        :param file: 音频url 或 bytes(将使用base64编码)
        :param use_cache: 使用缓存
        :return: CQ 码
        """
        code = '[CQ:record,file='
        if isinstance(file, str):
            code += f'{file}'
        elif isinstance(file, bytes):
            code += f'base64://{base_64(file)}'
        if use_cache == 0:
            code += ',cache=0'
        code += ']'
        return code

    @staticmethod
    def record_local(file_path: str, use_cache: bool = True) -> str:
        """语音消息
        [CQ:record,file=file:///1.mp3]
        使用本地文件

        :param file_path: 本地文件路径
        :param use_cache: 使用缓存
        :return: CQ 码
        """
        # TODO: 先发送文件至服务器
        try:
            with open(file_path, 'rb') as f:
                return CqCode.record(f.read(), use_cache)
        except FileExistsError:
            return CqCode.record(f'file:///{file_path}', use_cache)
