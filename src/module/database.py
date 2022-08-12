from peewee import SqliteDatabase

from module.global_dict import Global
from module.logger_ex import LoggerEx, LogLevel
from module.singleton_type import SingletonType


class Database(metaclass=SingletonType):
    def __init__(self):
        self.db: SqliteDatabase = SqliteDatabase('database.db')
        self.log = LoggerEx(self.__class__.__name__)
        if Global().debug_mode:
            self.log.set_level(LogLevel.DEBUG)
        self.log.debug(f'{self.__class__.__name__} initializing...')

    def connect(self):
        if self.db.connect():
            self.log.debug('connected')
        else:
            self.log.error('connection failed')
            raise ConnectionError('connection failed')
        self.db.create_tables([])

    def disconnect(self):
        if not self.db.close():
            self.log.error('disconnect failed')
        else:
            self.log.debug('disconnected')
