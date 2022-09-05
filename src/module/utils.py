import base64
import contextlib
import ctypes
import hashlib
import os
import platform
from datetime import datetime
from io import BytesIO, StringIO
from math import inf
from threading import Thread
from typing import Any, Generator, Union

import distro
import psutil
import qrcode
from PIL import Image
from pyzbar.pyzbar import decode as pyzbar_decode


def print_qrcode(text: str) -> None:
    """在控制台打印二维码"""
    qr = qrcode.QRCode()
    qr.add_data(text)
    with StringIO() as out:
        qr.print_ascii(out, invert=True)
        print(out.getvalue())


def decode_qrcode(file_data: bytes) -> str:
    """二维码解码"""
    with BytesIO() as bytes_io:
        bytes_io.write(file_data)
        with Image.open(bytes_io) as img:
            if a := pyzbar_decode(img):
                b = a[0]
                c = b.data
                return c.decode('utf-8')
    return ''


def base_64(file_data: bytes) -> str:
    """计算base64编码"""
    return base64.b64encode(file_data).decode()


def checksum(file: Union[str, bytes], hash_factory=hashlib.md5, chunk_num_blocks=128) -> str:
    """计算校验和
    :param file: 文件路径或文件内容
    :param hash_factory: 哈希算法
    :param chunk_num_blocks: 分块数
    """
    h = hash_factory()
    if isinstance(file, str):
        with open(file, 'rb') as _f:
            while chunk := _f.read(chunk_num_blocks * h.block_size):
                h.update(chunk)
    elif isinstance(file, bytes):
        h.update(file)
    else:
        raise TypeError(f'{type(file)} is not supported')
    return h.hexdigest()


def change_console_title(title: str) -> None:
    """Windows 平台修改控制台标题"""
    with contextlib.suppress(Exception):
        ctypes.windll.kernel32.SetConsoleTitleW(title)


def get_system_description() -> str:
    """获取系统版本"""
    system = platform.system().strip().lower()
    if system.startswith('win'):
        platform_system = 'Windows'
        platform_version = platform.version()
    else:
        platform_system = distro.name(True)
        platform_version = ''
    return f'{platform_system} {platform_version} {platform.machine().strip()}'


def get_system_memory_usage(round_: int = 4) -> float:
    """获取系统内存使用率

    :param round_: 保留小数位数
    """
    platform_memory = psutil.virtual_memory()
    platform_memory_usage = 1 - platform_memory.available / platform_memory.total
    platform_memory_usage *= 100
    return round(platform_memory_usage, round_)


def get_script_memory_usage(round_: int = 4) -> float:
    """获取脚本内存占用率

    :param round_: 保留小数位数
    """
    self_process = psutil.Process(os.getpid())
    return round(self_process.memory_percent(), round_)


def get_system_uptime() -> str:
    """获取系统运行时间

    :return: 系统运行时间 like: 24 days, 18:30:43
    """
    boot_time = datetime.fromtimestamp(psutil.boot_time())
    curr_time = datetime.now()
    uptime = curr_time - boot_time
    return str(uptime).split('.')[0]


def get_script_uptime() -> str:
    """获取脚本运行时间

    :return: 脚本运行时间 like: 24
    """
    self_process = psutil.Process(os.getpid())
    curr_time = datetime.now()
    start_time = self_process.create_time()
    start_time = datetime.fromtimestamp(start_time)
    uptime = curr_time - start_time
    return str(uptime).split('.')[0]


def kill_thread(thread: Thread) -> None:
    """强制结束线程，注意不得设计为类方法！"""
    exctype = SystemExit
    if not (thread.is_alive() and thread.ident):
        return
    tid = ctypes.c_long(thread.ident)
    res = ctypes.pythonapi.PyThreadState_SetAsyncExc(tid, ctypes.py_object(exctype))
    if res == 0:
        raise ValueError('invalid thread id')
    elif res != 1:
        ctypes.pythonapi.PyThreadState_SetAsyncExc(tid, None)
        raise SystemError('PyThreadState_SetAsyncExc failed')


def deep_iter(data: Any, depth=inf, current_depth=1) -> Generator[Any, None, None]:
    """
    递归深度遍历数据

    :param data: 数据
    :param depth: 遍历深度，默认无限深度
    :param current_depth: 当前深度
    """
    if isinstance(data, dict) and (depth and current_depth <= depth):
        for key, value in data.items():
            for child_path, child_value in deep_iter(value, depth=depth, current_depth=current_depth + 1):
                yield [key] + child_path, child_value
    else:
        yield [], data


def get_screenshot() -> bytes:
    """截屏"""
    from io import BytesIO

    from PIL import ImageGrab
    with BytesIO() as f:
        ImageGrab.grab(all_screens=True).save(f, 'PNG')
        f.seek(0)
        return f.read()


if __name__ == '__main__':
    for i in deep_iter({
        'a': {
            'b': {
                'c': 'd',
                'e': {
                    'f': 'g'
                }
            },
            'e': 'f'
        },
    }):
        print(i)
