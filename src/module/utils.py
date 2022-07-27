from io import BytesIO, StringIO

import qrcode
from PIL import Image
from pyzbar.pyzbar import decode as pyzbar_decode


def print_qrcode(text: str) -> None:
    qr = qrcode.QRCode()
    qr.add_data(text)
    with StringIO() as out:
        qr.print_ascii(out, invert=True)
        print(out.getvalue())


def decode_qrcode(file_data: bytes) -> str:
    with BytesIO() as bytes_io:
        bytes_io.write(file_data)
        with Image.open(bytes_io) as img:
            return pyzbar_decode(img)[0].data.decode('utf-8')


if __name__ == '__main__':
    # 假装是在内存中
    with open('qrcode.png', 'rb') as f:
        print(decode_qrcode(f.read()))
