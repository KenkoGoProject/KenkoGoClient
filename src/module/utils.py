import base64
import contextlib
import ctypes
import hashlib
import inspect
import os
import platform
from datetime import datetime
from io import BytesIO, StringIO
from threading import Thread
from typing import Union

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
    tid = ctypes.c_long(thread.ident)
    if not inspect.isclass(exctype):
        exctype = type(exctype)
    res = ctypes.pythonapi.PyThreadState_SetAsyncExc(tid, ctypes.py_object(exctype))
    if res == 0:
        raise ValueError('invalid thread id')
    elif res != 1:
        ctypes.pythonapi.PyThreadState_SetAsyncExc(tid, None)
        raise SystemError('PyThreadState_SetAsyncExc failed')


if __name__ == '__main__':
    print(psutil.Process(os.getpid()).memory_full_info())
