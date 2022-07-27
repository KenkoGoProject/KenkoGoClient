from module.client_api import ClientApi
from module.global_dict import Global
from module.logger_ex import LoggerEx, LogLevel
from module.plugin_manager import PluginManager
from module.server_api import ServerApi
from module.singleton_type import SingletonType
from module.utils import decode_qrcode, print_qrcode
from rich.table import Table


class CommandHandler(metaclass=SingletonType):
    def __init__(self):
        self.log = LoggerEx(self.__class__.__name__)
        if Global().debug_mode:
            self.log.set_level(LogLevel.DEBUG)

    def add(self, command):
        self.log.debug(f'Add command: {command}')
        if command == '/help':
            help_text = """支持的命令 Available commands:
/help: 显示此帮助 Show this help message
/exit: 退出KenkoGoClient Quit the application

/connect: 连接Server Connect to the server
/disconnect: 断开连接 Disconnect from the server

/info: 查看Client状态 Show the client status
/status: 查看Server状态 Show the server status

/start: 启动go-cqhttp Start go-cqhttp
/stop: 停止go-cqhttp Stop go-cqhttp
/qrcode: 显示登录二维码 Show qrcode of go-cqhttp

/list：列出插件信息 List plugins
/reload: 重载插件(未完成) Reload plugins(WIP)
/enable: 启用所有插件 Enable all plugins
/disable: 禁用所有插件 Disable all plugins
"""
            Global().console.print(help_text)
        elif command == '/exit':
            Global().time_to_exit = True
        elif command == '/connect':
            ClientApi().connect()
        elif command == '/disconnect':
            ClientApi().disconnect()
        elif command == '/start':
            ServerApi().start_instance()
        elif command == '/stop':
            ServerApi().stop_instance()
        elif command == '/qrcode':
            code = ServerApi().get_qrcode()
            if not code:
                self.log.error('Failed to get qrcode')
            code_url = decode_qrcode(code)
            print_qrcode(code_url)
        elif command == '/info':
            info = ClientApi().get_info()
            Global().console.pretty_print(info)
        elif command == '/status':
            status = ServerApi().get_status()
            Global().console.pretty_print(status)
        elif command == '/list':
            self.list_plugins()
        elif command == '/reload':
            self.log.info('Work in progress...')  # TODO: RELOAD PLUGINS
        elif command == '/enable':
            PluginManager().enable_all_plugin()
        elif command == '/disable':
            PluginManager().disable_all_plugin()
        else:
            self.log.error('Invalid Command')

    @staticmethod
    def list_plugins():
        table = Table(title='插件 Plugins')
        table.add_column('名称 Name', style='cyan', no_wrap=True)
        table.add_column('版本 Version', style='deep_sky_blue1')
        table.add_column('状态 Status', style='magenta')

        plugins = PluginManager().plugin_list
        for plugin in plugins:
            enable_str = '[green]已启用 Enabled' if plugin.enable else '[red]已禁用 Disabled'
            table.add_row(plugin.class_name, plugin.version, enable_str)

        Global().console.print(table)
