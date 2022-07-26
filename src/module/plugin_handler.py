from importlib import import_module
from pathlib import Path
from types import ModuleType
from typing import List

from inflection import camelize

from assets.plugin_entity import Plugin
from assets.simple_plugin import SimplePlugin
from module.global_dict import Global
from module.gocq_api import GocqApi
from module.logger_ex import LoggerEx, LogLevel
from module.singleton_type import SingletonType


class PluginHandler(metaclass=SingletonType):
    _plugins_loaded = False

    def __init__(self):
        self.log = LoggerEx(self.__class__.__name__)
        if Global().debug_mode:
            self.log.set_level(LogLevel.DEBUG)
        self.log.debug(f'{self.__class__.__name__} initializing...')
        self.plugin_list: List[Plugin] = []

    def load_plugins(self):
        self.log.debug('Initializing Plugins')
        plugin_dir = Path('plugin')
        for plugin_path in plugin_dir.iterdir():
            plugin_path = plugin_path.name  # 去除路径
            plugin_path = str(plugin_path)
            module_name = plugin_path.removesuffix('.py')  # 使得包也可以被导入
            if not module_name.endswith('_kenko'):
                continue  # 不以_kenko结尾的包/模块不被导入
            class_name = camelize(module_name.removesuffix('_kenko'))  # 将模块转换为类名
            module_name = f'plugin.{module_name}'
            self.log.debug(f'Loading plugin: [bold magenta]{class_name}', extra={'markup': True})
            try:
                module: ModuleType = import_module(module_name)
                class_: type = getattr(module, class_name)
            except ModuleNotFoundError:
                self.log.error(f'Module [bold magenta]{module_name} [red]not found', extra={'markup': True})
                continue
            except AttributeError:
                self.log.error(f'Class [bold magenta]{class_name} [red]not found', extra={'markup': True})
                continue
            try:
                object_: SimplePlugin = class_(GocqApi(class_name))
                plugin = Plugin(object_)
                plugin.name = object_.name
                plugin.description = object_.description
                plugin.version = object_.version
                self.log.debug(f'[magenta][{plugin.class_name}][/magenta]: '
                               f'{plugin.name}({plugin.version}) - {plugin.description}', extra={'markup': True})
                object_.init()
            except Exception as e:
                self.log.error(f'Plugin [bold magenta]{class_name}[/bold magenta] '
                               f'initialization [red]failed[/red]: {e}',
                               extra={'markup': True})
                continue
            self.plugin_list.append(plugin)
            self.log.info(f'[bold magenta]{class_name} [green]loaded', extra={'markup': True})
        self._plugins_loaded = True

    def enable_all_plugin(self):
        for plugin_ in self.plugin_list:
            try:
                plugin_.enable = plugin_.obj.on_enable() == plugin_.obj
            except Exception as e:
                self.log.error(f'{plugin_.class_name} error: {e}')
                continue
            if plugin_.enable:
                self.log.info(f'[green]Enabled [bold magenta]{plugin_.class_name} ', extra={'markup': True})
            else:
                self.log.error(f'[bold magenta]{plugin_.class_name} [red]enable failed', extra={'markup': True})

    def disable_all_plugin(self):
        for plugin_ in self.plugin_list:
            if not plugin_.enable:
                continue
            try:
                if plugin_.obj.on_before_disable() != plugin_.obj:
                    self.log.warning(f'[bold magenta]{plugin_.name} [red]not ready to be disabled',
                                     extra={'markup': True})
                    plugin_.enable = plugin_.obj.on_disable() != plugin_.obj
            except Exception as e:
                self.log.error(f'{plugin_.class_name} error: {e}')
                continue
            if plugin_.enable:
                self.log.debug(f'[bold magenta]{plugin_.name} [red]disable failed', extra={'markup': True})
                continue
            self.log.info(f'[orange]Disabled [bold magenta]{plugin_.name}', extra={'markup': True})

    def broadcast_message(self, message):
        for plugin_ in self.plugin_list:
            if not plugin_.enable:
                continue
            try:
                plugin_.obj.on_message(message)
            except Exception as e:
                self.log.error(f'{plugin_.name} error: {e}')

    def broadcast_connected(self):
        for plugin_ in self.plugin_list:
            if not plugin_.enable:
                continue
            try:
                plugin_.obj.on_connect()
            except Exception as e:
                self.log.error(f'{plugin_.name} error: {e}')

    def broadcast_disconnected(self):
        for plugin_ in self.plugin_list:
            if not plugin_.enable:
                continue
            try:
                plugin_.obj.on_disconnect()
            except Exception as e:
                self.log.error(f'{plugin_.name} error: {e}')

    def broadcast_event(self, event: str, *args, **kwargs):
        if event == 'message':
            self.broadcast_message(*args, **kwargs)
        elif event == 'connected':
            self.broadcast_connected()
        elif event == 'disconnected':
            self.broadcast_disconnected()
        else:
            raise ValueError(f'Unknown event: {event}')
