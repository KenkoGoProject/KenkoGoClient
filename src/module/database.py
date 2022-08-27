from typing import List, Optional, Type

from peewee import Model
from playhouse.apsw_ext import APSWDatabase

from assets.database_tables.friend_request import FriendRequest
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
        self.tables: List[Type[Model]] = [FriendRequest]
        for table in self.tables:
            # noinspection PyProtectedMember
            table._meta.database = self

    def connect(self, *args):
        if super().connect():
            self.log.debug('connected')
        else:
            self.log.error('connection failed')
            raise ConnectionError('connection failed')
        self.create_tables(self.tables)

    def close(self):
        if super().close():
            self.log.error('disconnect failed')
        else:
            self.log.debug('disconnected')

    @staticmethod
    def get_one_not_finish_friend_request_by_uuid(uuid) -> Optional[FriendRequest]:
        return FriendRequest.get_or_none(FriendRequest.uuid == uuid, FriendRequest.finish == False)  # noqa: E712
