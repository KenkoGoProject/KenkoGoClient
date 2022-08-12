from typing import Callable, Set

from module.singleton_type import SingletonType


class MessageConfig(metaclass=SingletonType):
    def __init__(self, save_function: Callable = None):
        self.save = save_function

        self.enable = False  # 是否启用
        self.administrators: Set[int] = set()  # 管理员，无条件响应
        self.block_self = False  # 是否屏蔽自己的消息
        self.block_group = False  # 是否屏蔽群消息
        self.block_private = False  # 是否屏蔽私聊消息

        self.ignore_users: Set[int] = set()  # 忽略的用户，直接交给插件
        self.block_users: Set[int] = set()  # 屏蔽的账号，使得插件不响应
        self.block_groups: Set[int] = set()  # 屏蔽的群，使得插件不响应

    def __setattr__(self, key, value):
        super(MessageConfig, self).__setattr__(key, value)
        if self.save and isinstance(self.save, Callable):
            self.save()

    def update(self, config: dict):
        for key, value in config.items():
            if key == 'enable':
                self.enable = value
            elif key == 'administrators':
                self.administrators = set(value)
            elif key == 'block_self':
                self.block_self = value
            elif key == 'block_group':
                self.block_group = value
            elif key == 'block_private':
                self.block_private = value
            elif key == 'ignore_users':
                self.ignore_users = set(value)
            elif key == 'block_users':
                self.block_users = set(value)
            elif key == 'block_groups':
                self.block_groups = set(value)

    def __len__(self) -> int:
        return len(self.to_dict())

    def to_dict(self) -> dict:
        return {
            'enable': self.enable,

            'administrators': self.administrators,
            'block_self': self.block_self,
            'block_group': self.block_group,
            'block_private': self.block_private,

            'ignore_users': self.ignore_users,
            'block_users': self.block_users,
            'block_groups': self.block_groups,
        }
