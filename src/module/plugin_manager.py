from importlib import import_module
from pathlib import Path
from types import ModuleType
from typing import List, Optional

from inflection import camelize

from assets.plugin_entity import Plugin
from assets.simple_plugin import SimplePlugin
from assets.test_plugin import TestPlugin
from module.client_api import ClientApi
from module.global_dict import Global
from module.gocq_api import GocqApi
from module.logger_ex import LoggerEx, LogLevel
from module.server_api import ServerApi
from module.singleton_type import SingletonType


class PluginManager(metaclass=SingletonType):
    """插件管理器"""

    def __init__(self):
        self.log = LoggerEx(self.__class__.__name__)
        if Global().debug_mode:
            self.log.set_level(LogLevel.DEBUG)
        self.log.debug(f'{self.__class__.__name__} initializing...')

        self.plugin_list: List[Plugin] = []  # 插件列表
        self._plugins_loaded = False  # 插件是否已经加载

    def load_plugin_from_disk(self, module_name: str) -> Optional[Plugin]:
        """加载插件

        :param module_name: 模块名，如 hello_world_kenko
        :return: 插件
        """
        class_name = camelize(module_name.removesuffix('_kenko'))  # 将模块转换为类名
        module_name = f'plugin.{module_name}'
        self.log.debug(f'Loading plugin: [bold magenta]{class_name}', extra={'markup': True})
        try:
            module: ModuleType = import_module(module_name)
            class_: type = getattr(module, class_name)
        except ModuleNotFoundError:
            self.log.error(f'Module [bold magenta]{module_name} [red]not found', extra={'markup': True})
            return None
        except AttributeError:
            self.log.error(f'Class [bold magenta]{class_name} [red]not found', extra={'markup': True})
            return None
        except Exception as e:
            self.log.exception(e)
            return None
        try:
            user_config = Global().user_config
            host_and_port = f'{user_config.host}:{user_config.port}'
            object_: SimplePlugin = class_(
                GocqApi(host_and_port, class_name),
                ClientApi(class_name),
                ServerApi(host_and_port, class_name)
            )
            if not object_.name:
                raise ValueError('插件信息名称错误，请检查！ [red]name is error')
            if not object_.description:
                raise ValueError('插件信息描述错误，请检查！ [red]description is error')
            if not object_.version or object_.version == '#error#':
                raise ValueError('插件信息版本错误，请检查！ [red]version is error')
            plugin = Plugin(object_)
            plugin.name = object_.name
            plugin.description = object_.description
            plugin.version = object_.version
            self.log.debug(f'[magenta]{plugin.class_name}[/magenta] __init__', extra={'markup': True})
            object_.on_initialize()
            return plugin
        except Exception as e:
            self.log.error(f'Plugin [bold magenta]{class_name}[/bold magenta] initialization [red]failed[/red]: {e}',
                           extra={'markup': True})
            return None

    def load_plugins(self) -> None:
        """加载所有插件"""
        self.log.debug('Initializing Plugins')
        plugin_dir = Path('plugin')
        for plugin_path in plugin_dir.iterdir():
            plugin_path = plugin_path.name  # 去除路径
            plugin_path = str(plugin_path)
            module_name = plugin_path.removesuffix('.py')  # 使得包也可以被导入
            if not module_name.endswith('_kenko'):
                continue  # 不以_kenko结尾的包/模块不被导入
            plugin: Plugin = self.load_plugin_from_disk(module_name)
            if not plugin:
                continue
            self.plugin_list.append(plugin)
            self.log.info(f'[bold magenta]{plugin.class_name}[/bold magenta] [green]loaded[/green]: '
                          f'{plugin.name}({plugin.version}) - {plugin.description}', extra={'markup': True})

        # 测试模式下加载测试插件
        if Global().test_mode:
            user_config = Global().user_config
            host_and_port = f'{user_config.host}:{user_config.port}'

            test_name = 'TestPlugin'
            test_plugin = TestPlugin(
                GocqApi(host_and_port, test_name),
                ClientApi(test_name),
                ServerApi(host_and_port, test_name)
            )
            self.plugin_list.append(Plugin(test_plugin))

        self._plugins_loaded = True

    def enable_all_plugin(self) -> None:
        """启用所有插件"""
        for plugin_ in self.plugin_list:
            if plugin_.enable:
                continue
            self.enable_plugin(plugin_)

    def enable_plugin(self, plugin: Plugin) -> None:
        """启用插件

        :param plugin: 插件
        :return: None
        """
        try:
            plugin.enable = plugin.obj.on_enable() == plugin.obj
        except Exception as e:
            self.log.exception(e)
            plugin.enable = False
        if plugin.enable:
            self.log.info(f'[green]Enabled [bold magenta]{plugin.class_name} ', extra={'markup': True})
        else:
            self.log.error(f'[bold magenta]{plugin.class_name} [red]enable failed', extra={'markup': True})

    def disable_all_plugin(self) -> None:
        """禁用所有插件"""
        for plugin_ in self.plugin_list:
            if not plugin_.enable:
                continue
            self.disable_plugin(plugin_)

    def reload_all_plugin(self) -> None:
        """重新加载所有插件"""
        ...  # TODO: 实现重新加载插件

    def disable_plugin(self, plugin: Plugin) -> None:
        """禁用插件

        :param plugin: 插件
        :return: None
        """
        try:
            if plugin.obj.on_before_disable() != plugin.obj:
                self.log.warning(f'[bold magenta]{plugin.name} [red]not ready to be disabled',
                                 extra={'markup': True})
            # TODO: 应该在这里先禁用插件，使得插件无法调用 API
            plugin.enable = plugin.obj.on_disable() != plugin.obj
        except Exception as e:
            self.log.exception(e)
            # TODO: 在这里要重新判断 enable 状态
        if plugin.enable:
            self.log.error(f'[bold magenta]{plugin.class_name} [red]disable failed', extra={'markup': True})
        else:
            self.log.info(f'[orange1]Disabled [bold magenta]{plugin.class_name}', extra={'markup': True})

    def polling_message(self, message: dict) -> None:
        """插件调用 on_message

        :param message: 消息
        :return: None
        """
        for plugin_ in self.plugin_list:
            if not plugin_.enable:
                continue
            try:
                if plugin_.obj.on_message(message) is not True:
                    break
            except Exception as e:
                self.log.exception(e)

    def polling_connected(self) -> None:
        """插件调用 on_connect"""
        for plugin_ in self.plugin_list:
            if not plugin_.enable:
                continue
            try:
                plugin_.obj.on_connect()
            except Exception as e:
                self.log.exception(e)

    def polling_disconnected(self) -> None:
        """插件调用 on_disconnect"""
        for plugin_ in self.plugin_list:
            if not plugin_.enable:
                continue
            try:
                plugin_.obj.on_disconnect()
            except Exception as e:
                self.log.exception(e)

    def polling_event(self, event: str, *args, **kwargs) -> None:
        """向所有插件发送事件"""
        if event == 'message':
            self.polling_message(*args, **kwargs)
        elif event == 'connected':
            self.polling_connected()
        elif event == 'disconnected':
            self.polling_disconnected()
        else:
            raise ValueError(f'Unknown event: {event}')
