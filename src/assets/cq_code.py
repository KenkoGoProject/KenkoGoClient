import base64


class CqCode:
    """CQ码生成器"""
    @staticmethod
    def face(face_id: int):
        return f'[CQ:face,id={face_id}]'

    @staticmethod
    def image(file, image_type: str = 'normal', use_cache: bool = True, show_id: int = 40000, threads: int = 2):
        code = '[CQ:image,file='
        if isinstance(file, str):
            code += f'{file}'
        elif isinstance(file, bytes):
            code += f'base64://{base64.b64encode(file).decode()}'
        if image_type == 'flash':
            code += ',type=flash'
        elif image_type == 'show':
            code += ',type=show'
            code += f',id={show_id}'
        if use_cache == 0:
            code += ',cache=0'
        code += f',c={threads}]'
        return code

    @staticmethod
    def image_local(file_path: str, image_type: str = 'normal',
                    use_cache: bool = True, show_id: int = 40000, threads: int = 2):
        try:
            with open(file_path, 'rb') as f:
                return CqCode.image(f.read(), image_type, use_cache, show_id, threads)
        except FileExistsError:
            return CqCode.image(f'file:///{file_path}', image_type, use_cache, show_id, threads)

    @staticmethod
    def at(user_id):
        """[CQ:at,qq=10001000]"""
        return f'[CQ:at,qq={user_id}]'

    @staticmethod
    def record(file, use_cache: bool = True):
        """[CQ:record,file=http://baidu.com/1.mp3]"""
        code = '[CQ:record,file='
        if isinstance(file, str):
            code += f'{file}'
        elif isinstance(file, bytes):
            code += f'base64://{base64.b64encode(file).decode()}'
        if use_cache == 0:
            code += ',cache=0'
        code += ']'
        return code

    @staticmethod
    def record_local(file_path: str, use_cache: bool = True):
        try:
            with open(file_path, 'rb') as f:
                return CqCode.record(f.read(), use_cache)
        except FileExistsError:
            return CqCode.record(f'file:///{file_path}', use_cache)
