import json
from importlib import import_module
from json import JSONDecodeError
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
    """插件管理器

    插件加载流程：
    1. 读取以前保存的插件状态：模块名、是否启用
    2. 读取配置中未保存的插件：模块名
    3. 加载列表中的模块
    """

    def __init__(self):
        self.log = LoggerEx(self.__class__.__name__)
        if Global().debug_mode:
            self.log.set_level(LogLevel.DEBUG)
        self.log.debug(f'{self.__class__.__name__} initializing...')

        self.plugin_list: List[Plugin] = []  # 插件列表
        self.plugins_loaded = False  # 插件是否已经加载
        self.local_config_path = Path(Global().root_dir, 'plugin.json')  # 插件配置文件路径

    def save_config(self) -> bool:
        """保存插件配置"""
        self.log.debug('Saving plugin config...')
        try:
            dict_to_save = [plugin.to_dict() for plugin in self.plugin_list if plugin.module_name != 'test_plugin']
            with self.local_config_path.open('w') as f:
                json.dump(dict_to_save, f, indent=4)
        except Exception as e:
            self.log.exception(e)
            return False
        return True

    def load_config(self) -> bool:
        """加载已保存的插件配置"""
        try:
            with self.local_config_path.open('r') as f:
                saved_config = json.load(f)
                self.log.debug(f'Saved config: {saved_config}')
        except FileNotFoundError:
            self.log.debug(f'[bold magenta]{self.local_config_path} [red]not found', extra={'markup': True})
            return True
        except JSONDecodeError:
            self.log.warning(f'[bold magenta]{self.local_config_path} [red]invalid', extra={'markup': True})
            return False
        except Exception as e:
            self.log.exception(e)
            return False
        self.plugin_list = []
        for saved_plugin in saved_config:
            try:
                new_plugin = Plugin(saved_plugin['module_name'])
                new_plugin.should_enable = saved_plugin['should_enable']
            except Exception as e:
                self.log.exception(e)
            else:
                self.plugin_list.append(new_plugin)
        return True

    def initialize_modules(self) -> None:
        """从模块加载插件"""
        user_config = Global().user_config
        host_and_port = f'{user_config.host}:{user_config.port}'

        for plugin in self.plugin_list:
            class_name = camelize(plugin.module_name.removesuffix('_kenko'))  # 将模块转换为类名
            plugin.class_name = class_name
            module_name = f'plugin.{plugin.module_name}'
            self.log.debug(f'Loading module: [bold magenta]{class_name}', extra={'markup': True})
            try:
                module: ModuleType = import_module(module_name)
            except Exception as e:
                self.log.exception(e)
                continue
            if not hasattr(module, class_name):
                self.log.error(f'Class [bold magenta]{class_name} [red]not found',
                               extra={'markup': True})
                continue
            class_: type = getattr(module, class_name)
            try:
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
            except Exception as e:
                self.log.error(
                    f'Plugin [bold magenta]{class_name}[/bold magenta] initialization [red]failed[/red]: {e}',
                    extra={'markup': True})
                continue
            plugin.name = object_.name
            plugin.description = object_.description
            plugin.version = object_.version
            plugin.obj = object_
            plugin.loaded = True
            self.log.debug(f'[magenta]{plugin.class_name}[/magenta] initialized', extra={'markup': True})
            try:
                init_ok = object_.on_initialize() == object_
            except Exception as e:
                self.log.error(f'Plugin [bold magenta]{class_name}[/bold magenta] initializing [red]failed[/red]: {e}',
                               extra={'markup': True})
                continue
            if init_ok:
                self.log.debug(f'Plugin [bold magenta]{class_name}[/bold magenta] initialized',
                               extra={'markup': True})
                plugin.initialized = True
        self.save_config()

        # 测试模式下加载测试插件
        if Global().test_mode:
            test_plugin = Plugin('test_plugin')
            test_plugin.should_enable = True
            test_plugin.class_name = 'TestPlugin'
            try:
                test_plugin.obj = TestPlugin(
                    GocqApi(host_and_port, test_plugin.class_name),
                    ClientApi(test_plugin.class_name),
                    ServerApi(host_and_port, test_plugin.class_name)
                )
            except Exception as e:
                self.log.exception(e)
                return
            test_plugin.name = test_plugin.obj.name
            test_plugin.description = test_plugin.obj.description
            test_plugin.version = test_plugin.obj.version
            test_plugin.loaded = True
            try:
                init_ok = test_plugin.obj.on_initialize() == test_plugin.obj
            except Exception as e:
                self.log.exception(e)
                return
            if init_ok:
                test_plugin.initialized = True
                self.plugin_list.append(test_plugin)

    def load_local_modules(self) -> None:
        """加载本地的模块"""
        self.log.debug('Loading local modules')
        plugin_dir = Path('plugin')
        for plugin_path in plugin_dir.iterdir():
            plugin_path = plugin_path.name  # 去除路径
            plugin_path = str(plugin_path)
            module_name = plugin_path.removesuffix('.py')  # 使得包也可以被导入
            if not module_name.endswith('_kenko'):
                continue  # 不以_kenko结尾的包/模块不被导入
            for plugin in self.plugin_list:
                if plugin.module_name == module_name:
                    break
            else:
                plugin = Plugin(module_name)
                self.plugin_list.append(plugin)
                self.log.debug(f'New module [magenta]{module_name}[/magenta] loaded', extra={'markup': True})

    def enable_plugins(self, all_=False) -> None:
        """启用插件"""
        for plugin_ in self.plugin_list:
            if (not plugin_.loaded) or (not plugin_.initialized) or plugin_.enable:
                continue
            if not all_ and not plugin_.should_enable:
                continue
            self.enable_plugin(plugin_)

    def disable_all_plugin(self) -> None:
        """禁用所有插件"""
        for plugin_ in self.plugin_list:
            if not plugin_.enable:
                continue
            self.disable_plugin(plugin_)

    def get_plugin(self, name: str) -> Optional[Plugin]:
        """通过名称获取已加载的插件"""
        return next(
            (plugin_ for plugin_ in self.plugin_list
             if plugin_.name == name
             or plugin_.class_name == name
             or plugin_.module_name == name),
            None
        )

    def enable_plugin(self, plugin: Plugin) -> bool:
        """启用插件

        :param plugin: 插件
        :return: 是否启用成功
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
        self.save_config()
        plugin.should_enable = plugin.enable
        return plugin.enable

    def disable_plugin(self, plugin: Plugin) -> bool:
        """禁用插件

        :param plugin: 插件
        :return: 是否禁用成功
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
        self.save_config()
        plugin.should_enable = plugin.enable
        return not plugin.enable

    def move_up_plugin(self, plugin: Plugin) -> bool:
        """向上移动插件

        :param plugin: 插件
        :return: 是否移动成功
        """
        for index, plugin_ in enumerate(self.plugin_list):
            if plugin_ == plugin:
                old_index = index
                break
        else:
            return False
        if old_index == 0:
            return False
        self.plugin_list.remove(plugin)
        self.plugin_list.insert(old_index - 1, plugin)
        self.save_config()
        return True

    def move_down_plugin(self, plugin: Plugin) -> bool:
        """向下移动插件

        :param plugin: 插件
        :return: 是否移动成功
        """
        for index, plugin_ in enumerate(self.plugin_list):
            if plugin_ == plugin:
                old_index = index
                break
        else:
            return False
        if old_index == len(self.plugin_list) - 1:
            return False
        self.plugin_list.remove(plugin)
        self.plugin_list.insert(old_index + 1, plugin)
        self.save_config()
        return True

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
