from importlib import import_module
from pathlib import Path
from types import ModuleType
from typing import List

from inflection import camelize

from assets.simple_plugin import SimplePlugin
from module.global_dict import Global
from module.gocq_api import GocqApi
from module.logger_ex import LoggerEx, LogLevel
from module.singleton_type import SingletonType


class Plugin:
    def __init__(self, obj: SimplePlugin):
        self.name = obj.__class__.__name__
        self.ready = False
        self.plugin: SimplePlugin = obj
        self.enable = False


class PluginHandler(metaclass=SingletonType):
    plugins_loaded = False

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
            if not plugin_path.is_file():
                continue
            plugin_path = plugin_path.name
            plugin_path = str(plugin_path)
            if not plugin_path.endswith('_kenko.py'):
                continue
            plugin_path = plugin_path.removesuffix('_kenko.py')
            module_name = f'plugin.{plugin_path}_kenko'
            class_name = camelize(plugin_path)
            self.log.debug(f'Loading plugin: [bold magenta]{class_name}', extra={'markup': True})
            try:
                module: ModuleType = import_module(module_name)
                class_: type = getattr(module, class_name)
                object_: SimplePlugin = class_(GocqApi(class_name))
                self.plugin_list.append(Plugin(object_))
            except ModuleNotFoundError:
                self.log.error(f'Module {module_name} not found')
                continue
        self.plugins_loaded = True

    def enable_plugins(self):
        for plugin_ in self.plugin_list:
            plugin_.enable = plugin_.plugin.on_enable()
            if plugin_.enable:
                self.log.debug(f'{plugin_.name} enabled')
            else:
                self.log.debug(f'{plugin_.name} not enabled')

    def disable_plugins(self):
        for plugin_ in self.plugin_list:
            if not plugin_.enable:
                continue
            plugin_.plugin.on_before_disable()
            plugin_.enable = False
            plugin_.plugin.on_disable()
            self.log.debug(f'{plugin_.name} disabled')

    def broadcast_message(self, message):
        for plugin_ in self.plugin_list:
            if not plugin_.enable:
                continue
            try:
                plugin_.plugin.on_message(message)
            except Exception as e:
                self.log.error(f'{plugin_.name} error: {e}')

    def broadcast_event(self, event: str, *args, **kwargs):
        if event == 'message':
            self.broadcast_message(*args, **kwargs)
        raise ValueError(f'Unknown event: {event}')

