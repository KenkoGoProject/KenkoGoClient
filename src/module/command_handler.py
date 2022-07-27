from module.client_api import ClientApi
from module.global_dict import Global
from module.logger_ex import LoggerEx, LogLevel
from module.server_api import ServerApi
from module.singleton_type import SingletonType
from module.utils import decode_qrcode, print_qrcode


class CommandHandler(metaclass=SingletonType):
    def __init__(self):
        self.log = LoggerEx(self.__class__.__name__)
        if Global().debug_mode:
            self.log.set_level(LogLevel.DEBUG)

    def add(self, command):
        self.log.debug(f'Add command: {command}')
        if command == '/help':
            help_text = """Available commands:
/help: 显示此帮助  Show this help message
/exit: 退出KenkoGoClient  Quit the application
/sstatus: 查看KenkoGoServer状态  Show the server status
/cstatus: 查看Client状态  Show the client status
/start: 启动go-cqhttp  Start go-cqhttp
/stop: 停止go-cqhttp  Stop go-cqhttp
/qrcode: 显示登录二维码  Show qrcode of go-cqhttp
"""
            Global().console.print(help_text)
        elif command == '/exit':
            Global().time_to_exit = True
        elif command == '/stop':
            ServerApi().stop_instance()
        elif command == '/start':
            ServerApi().start_instance()
        elif command == '/qrcode':
            code = ServerApi().get_qrcode()
            if not code:
                self.log.error('Failed to get qrcode')
            code_url = decode_qrcode(code)
            print_qrcode(code_url)
        elif command == '/sstatus':
            status = ServerApi().get_status()
            if isinstance(status, dict):
                Global().console.pretty_print(status)
            else:
                self.log.error(f'Failed to get server status: {status}')
        elif command == '/cstatus':
            Global().console.pretty_print(ClientApi().get_info())
        else:
            self.log.error('Invalid Command')
