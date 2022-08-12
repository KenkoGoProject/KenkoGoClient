import base64
import contextlib
import hashlib
import ctypes
from io import BytesIO, StringIO
from typing import Union

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


if __name__ == '__main__':
    # 假装是在内存中
    with open('qrcode.png', 'rb') as f:
        print(decode_qrcode(f.read()))
