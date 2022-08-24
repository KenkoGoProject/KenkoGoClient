from typing import Callable, Set

from module.singleton_type import SingletonType


class MessageConfig(metaclass=SingletonType):
    def __init__(self, save_function: Callable = None):
        self.save = save_function or (lambda: None)

        self.enable = False  # 是否启用
        self.block_self = False  # 是否屏蔽自己的消息
        self.command_prefix = '!'  # 命令前缀
        self.administrators: Set[int] = set()  # 管理员，无条件响应
        self.block_private = False  # 是否屏蔽私聊消息
        self.block_group = False  # 是否屏蔽群消息
        self.block_guild = False  # 是否屏蔽频道消息
        self.block_friend_request = False  # 是否屏蔽好友请求
        self.block_group_invite = False  # 是否屏蔽群邀请

        self.whitelist_mode = False  # 白名单模式，仅响应白名单
        self.whitelist_users: Set[int] = set()  # 白名单用户
        self.whitelist_groups: Set[int] = set()  # 白名单群

        self.block_users: Set[int] = set()  # 屏蔽的账号，使得插件不响应
        self.block_groups: Set[int] = set()  # 屏蔽的群，使得插件不响应

    def to_dict(self) -> dict:
        return {
            'enable': self.enable,

            'block_self': self.block_self,
            'command_prefix': self.command_prefix,
            'administrators': self.administrators,
            'block_private': self.block_private,
            'block_group': self.block_group,
            'block_guild': self.block_guild,
            'block_friend_request': self.block_friend_request,
            'block_group_invite': self.block_group_invite,

            'whitelist_mode': self.whitelist_mode,
            'whitelist_users': self.whitelist_users,
            'whitelist_groups': self.whitelist_groups,

            'block_users': self.block_users,
            'block_groups': self.block_groups,
        }

    def __setattr__(self, key, value):
        super(MessageConfig, self).__setattr__(key, value)
        if self.save and isinstance(self.save, Callable):
            self.save()

    def update(self, config: dict):
        for key, value in config.items():
            if hasattr(self, key):
                t = type(getattr(self, key))
                setattr(self, key, t(value))

    def __len__(self) -> int:
        return len(self.to_dict())
