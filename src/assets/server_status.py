from enum import Enum


class ServerStatus(Enum):
    """服务器状态码"""
    STOPPED = 0.1  # 未启动
    HTTP_THREAD_STARTED = 0.2  # HTTP线程已启动
    STARTING = 1.1  # 已启动，等待下一个状态
    CONNECTING_TO_TENCENT = 1.2  # 已启动，正在连接腾讯服务器
    CONNECT_FAILED = 1.25  # 已启动，登录时发生致命错误
    GETTING_QRCODE = 1.3  # 已启动，正在获取二维码
    WAIT_FOR_SCAN = 1.4  # 已启动，等待扫码
    WAIT_FOR_CONFIRM = 1.45  # 已扫码，等待确认
    QRCODE_CANCELED = 1.46  # 已扫码，等待确认，用户取消了
    QRCODE_EXPIRED = 1.5  # 已启动，二维码过期
    FAIL_TO_FETCH_QRCODE = 1.6  # 已启动，获取二维码失败
    LOGGED_IN = 2.1  # 已启动，已登录，等待消息上报
    RUNNING = 3.1  # 已启动，运行中
    OFFLINE = 3.2  # 已启动，离线状态
    STOPPING = 4.1  # 已启动，正在停止
