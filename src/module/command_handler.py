from rich.table import Table

from module.client_api import ClientApi
from module.global_dict import Global
from module.logger_ex import LoggerEx, LogLevel
from module.plugin_manager import PluginManager
from module.server_api import ServerApi
from module.singleton_type import SingletonType
from module.utils import decode_qrcode, print_qrcode

HELP_TEXT = """支持的命令 Available commands:
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
/reload <name>: 重载插件 Reload plugins
/enable <name>: 启用插件 Enable plugin
/disable <name>: 禁用插件 Disable plugin
/up <name>: 上移插件 Move plugin up
/down <name>: 下移插件 Move plugin down
"""


class CommandHandler(metaclass=SingletonType):
    def __init__(self):
        self.log = LoggerEx(self.__class__.__name__)
        if Global().debug_mode:
            self.log.set_level(LogLevel.DEBUG)

    def add(self, command: str) -> None:
        self.log.debug(f'Get command: {command}')
        if command in {'/help', '/h'}:
            Global().console.print(HELP_TEXT)
        elif command == '/exit':
            Global().time_to_exit = True
        elif command == '/connect':
            ClientApi(self.__class__.__name__).connect()
        elif command == '/disconnect':
            ClientApi(self.__class__.__name__).disconnect()
        elif command == '/start':
            self.start_instance()
        elif command == '/stop':
            self.stop_instance()
        elif command in {'/qrcode', '/qr'}:
            self.print_qrcode()
        elif command == '/info':
            info = ClientApi(self.__class__.__name__).get_info()
            Global().console.print_object(info)
        elif command == '/status':
            self.print_server_status()
        elif command in {'/list', '/ls', 'ls'}:
            self.list_plugins()
        elif command.startswith('/reload '):
            command = command.removeprefix('/reload ').strip()
            self.reload_plugin(command)
        elif command.startswith('/r '):
            command = command.removeprefix('/r ').strip()
            self.reload_plugin(command)
        elif command.startswith('/enable '):
            command = command.removeprefix('/enable ').strip()
            self.enable_plugin(command)
        elif command.startswith('/disable '):
            command = command.removeprefix('/disable ').strip()
            self.disable_plugin(command)
        elif command.startswith('/up '):
            command = command.removeprefix('/up ').strip()
            self.up_plugin(command)
        elif command.startswith('/down '):
            command = command.removeprefix('/down ').strip()
            self.down_plugin(command)
        else:
            self.log.error('Invalid Command')

    def enable_plugin(self, name) -> None:
        if not name:
            return
        if not (plugin := PluginManager().get_plugin(name)):
            self.log.error(f'Plugin {name} not found')
            return
        PluginManager().enable_plugin(plugin)

    def disable_plugin(self, name) -> None:
        if not name:
            return
        if not (plugin := PluginManager().get_plugin(name)):
            self.log.error(f'Plugin {name} not found')
            return
        PluginManager().disable_plugin(plugin)

    def up_plugin(self, name):
        if not name:
            return
        if not (plugin := PluginManager().get_plugin(name)):
            self.log.error(f'Plugin {name} not found')
            return
        if not PluginManager().move_up_plugin(plugin):
            self.log.error(f'Plugin {name} is already at the top')
            return

    def down_plugin(self, name):
        if not name:
            return
        if not (plugin := PluginManager().get_plugin(name)):
            self.log.error(f'Plugin {name} not found')
            return
        if not PluginManager().move_down_plugin(plugin):
            self.log.error(f'Plugin {name} is already at the bottom')
            return

    def reload_plugin(self, name):
        if not name:
            return
        if not (plugin := PluginManager().get_plugin(name)):
            self.log.error(f'Plugin {name} not found')
            return
        if not PluginManager().reinitialize_module(plugin):
            self.log.error(f'Plugin {name} failed to reload')

    def start_instance(self) -> None:
        """启动go-cqhttp"""
        user_config = Global().user_config
        host = user_config.host
        port = user_config.port
        token = user_config.token
        api = ServerApi(f'{host}:{port}', token, self.__class__.__name__)
        api.start_instance()

    def stop_instance(self) -> None:
        """停止go-cqhttp"""
        user_config = Global().user_config
        host = user_config.host
        port = user_config.port
        token = user_config.token
        api = ServerApi(f'{host}:{port}', token, self.__class__.__name__)
        api.stop_instance()

    def print_qrcode(self) -> None:
        user_config = Global().user_config
        host = user_config.host
        port = user_config.port
        token = user_config.token
        api = ServerApi(f'{host}:{port}', token, self.__class__.__name__)
        code = api.get_qrcode()
        if not code:
            self.log.error('Failed to get qrcode')
        if code_url := decode_qrcode(code):
            print_qrcode(code_url)
        else:
            self.log.error('Failed to decode qrcode')

    def print_server_status(self) -> None:
        user_config = Global().user_config
        host = user_config.host
        port = user_config.port
        token = user_config.token
        api = ServerApi(f'{host}:{port}', token, self.__class__.__name__)
        status = api.get_status()
        Global().console.print_object(status)

    @staticmethod
    def list_plugins() -> None:
        """在控制台打印插件列表"""
        table = Table(title='插件 Plugins')
        table.add_column('序号 Number', justify='right')
        table.add_column('名称 Name', style='cyan')
        table.add_column('版本 Version', style='deep_sky_blue1')
        table.add_column('状态 Status', style='magenta')

        plugins = PluginManager().plugin_list
        for num, plugin in enumerate(plugins):
            if not plugin.loaded:
                continue
            enable_str = '[green]已启用 Enabled' if plugin.enable else '[red]已禁用 Disabled'
            table.add_row(str(num + 1), plugin.class_name, plugin.version, enable_str)

        Global().console.print(table)
