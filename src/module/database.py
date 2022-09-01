from typing import List, Optional, Type

from peewee import Model
from playhouse.apsw_ext import APSWDatabase
from playhouse.kv import KeyValue

from assets.database_tables.friend_request import FriendRequest
from assets.database_tables.group_invite import GroupInvite
from module.global_dict import Global
from module.logger_ex import LoggerEx, LogLevel
from module.singleton_type import SingletonType


class Database(APSWDatabase, metaclass=SingletonType):
    def sequence_exists(self, seq):
        raise NotImplementedError

    def __init__(self):
        super().__init__('database.db')
        self.log = LoggerEx(self.__class__.__name__)
        if Global().debug_mode:
            self.log.set_level(LogLevel.DEBUG)
        self.log.debug(f'{self.__class__.__name__} initializing...')
        self.tables: List[Type[Model]] = [FriendRequest, GroupInvite]
        self.bind(self.tables)
        self.KV: Optional[KeyValue] = None
        self.UUIDS: Optional[KeyValue] = None

    def connect(self, *args):
        if super().connect():
            self.log.debug('connected')
        else:
            self.log.error('connection failed')
            raise ConnectionError('connection failed')
        self.create_tables(self.tables)
        self.KV = KeyValue(database=self, table_name='kv')
        self.UUIDS = KeyValue(database=self, table_name='uuids')
        del self.UUIDS[self.UUIDS.value == 0]

    def close(self):
        del self.UUIDS[self.UUIDS.value == 0]
        self.KV = None
        self.UUIDS = None
        if super().close():
            self.log.debug('disconnected')
        else:
            self.log.error('disconnect failed')
