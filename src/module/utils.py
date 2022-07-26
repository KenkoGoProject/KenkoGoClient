import hashlib
import hmac
import platform
import random
import re
import socket
from pathlib import Path, PurePath
from re import Pattern
from typing import AnyStr

import requests
from rich.progress import track

from assets.os_type import OSType
from module.atomicwrites import atomic_write
from module.exception_ex import UnknownSystemError


def is_port_in_use(_port: int, _host: str = '127.0.0.1') -> bool:
    """检查端口是否被占用

    :param _port: 端口号
    :param _host: 主机名
    :return: True/False
    """
    s = None
    try:
        s = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
        s.settimeout(1)
        s.connect((_host, _port))
        return True
    except socket.error:
        return False
    finally:
        if s:
            s.close()


def get_random_free_port(min_: int = 10000, max_: int = 65535) -> int:
    """获取一个随机空闲端口

    :param min_: 最小端口号
    :param max_: 最大端口号
    :return: 空闲端口号
    """
    result = random.randint(min_, max_)
    while is_port_in_use(result):
        result = random.randint(min_, max_)
    return result


def get_self_ip() -> str:
    """获取自身ip

    https://www.zhihu.com/question/49036683/answer/124321702
    """
    s = None
    try:
        import socket
        s = socket.socket(socket.AF_INET, socket.SOCK_DGRAM)
        s.connect(('8.8.8.8', 80))
        return s.getsockname()[0]
    finally:
        if s:
            s.close()


def get_hmac(key: str, content: bytes, alg=hashlib.sha1) -> str:
    """获取hmac

    :param key: 密钥
    :param content: 内容
    :param alg: 加密算法
    :return: hmac
    """
    hmac_code = hmac.new(key.encode(), content, alg)
    return hmac_code.hexdigest()


def copy_property(dict_: dict, obj: object) -> None:
    """复制属性，将dict中出现并且对象属性中存在同名的进行拷贝

    :param dict_: 来源字典
    :param obj: 目标对象
    :return: None
    """
    # TODO: 这里只能转换一层...
    for key, value in dict_.items():
        if hasattr(obj, key):
            setattr(obj, key, value)


def dict_to_object(dict_: dict, class_: type) -> object:
    """将字典转换为类实例

    :param dict_: 字典
    :param class_: 类
    :return: 对象
    """
    obj = class_()
    copy_property(dict_, obj)
    return obj


def get_os_type() -> OSType:
    """获取系统类型"""
    system = platform.system().strip().lower()
    arch = platform.machine().strip().lower()
    if system.startswith('win'):
        if arch.startswith('amd64') or arch.startswith('x86_64'):
            return OSType.WINDOWS_AMD64
    elif system.startswith('lin'):
        if arch.startswith('amd64') or arch.startswith('x86_64'):
            return OSType.LINUX_AMD64
    raise UnknownSystemError(f'Unknown system: {system} {arch}')


def os_type_to_asset_finder(type_: OSType) -> Pattern[AnyStr]:
    """获取系统类型对应的 go-cqhttp 发行版正则匹配器"""
    if type_ == OSType.WINDOWS_AMD64:
        return re.compile(r'win.+amd64.*\.zip')  # type: ignore[arg-type]
    elif type_ == OSType.WINDOWS_I386:
        return re.compile(r'win.+386.*\.zip')  # type: ignore[arg-type]
    elif type_ == OSType.LINUX_AMD64:
        return re.compile(r'linux.+amd64.*tar\.gz')  # type: ignore[arg-type]
    elif type_ == OSType.LINUX_I386:
        return re.compile(r'linux.+386.*tar\.gz')  # type: ignore[arg-type]
    raise UnknownSystemError(f'Unknown system: {type_}')


def download_file(url: str, file_path: str) -> None:
    """下载文件并显示进度条

    :param url: 文件url
    :param file_path: 文件路径，需包含文件名，会覆盖已有文件
    """
    file = Path(file_path)
    if file.is_dir() or file.is_symlink():
        raise FileExistsError(f'{file_path} is a directory or a symbolic link')
    if file.exists():
        file.unlink()
    file.parent.mkdir(parents=True, exist_ok=True)
    r = requests.get(url, stream=True)
    tracker = track(
        r.iter_content(chunk_size=1024),
        description=f'[bold blue]{PurePath(file_path).name}',
        total=int(r.headers['Content-Length']) // 1024
    )
    with atomic_write(file_path, mode='wb') as f:
        for chunk in tracker:
            if chunk:
                f.write(chunk)
