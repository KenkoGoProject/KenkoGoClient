from datetime import datetime
from typing import List, Optional, Union
from uuid import uuid4

from playhouse.apsw_ext import (BooleanField, CharField, DateTimeField,
                                IntegerField)

from assets.database_tables.base_model import BaseModel


class FriendRequest(BaseModel):
    flag: str = CharField(primary_key=True)
    user_id: int = IntegerField()
    comment: str = CharField()
    is_finish: bool = BooleanField(default=False)
    finish_by: int = IntegerField(null=True)
    finish_at: datetime = DateTimeField(null=True)
    uuid: Optional[str] = CharField(null=True, unique=True)

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        uuid: str = str(uuid4().int)[:7]
        if uuid not in self.UUIDS:
            self.UUIDS[uuid] = 0
            self.uuid = uuid

    created_at: datetime = DateTimeField(default=datetime.now, null=True)
    updated_at: datetime = DateTimeField(default=datetime.now, null=True)

    class Meta:
        table_name = 'friend_request'

    # noinspection PyMethodOverriding
    def save(self, update=False) -> Union[bool, int]:
        if update:
            self.updated_at = datetime.now()
        self.UUIDS[self.uuid] = 1
        return super().save(not update)

    def finish(self, user_id) -> Union[bool, int]:
        """
        完成好友申请

        :param user_id: 完成者的QQ号
        :return: 影响的行数
        """
        self.is_finish = True
        self.finish_by = user_id
        del self.UUIDS[self.uuid]
        r = self.save(True)
        self.finish_at = datetime.now()
        self.uuid = None
        return r

    @classmethod
    def get_all_not_finish(cls) -> List['FriendRequest']:
        """获取所有未完成的好友申请"""
        return cls.select().where(cls.is_finish == False)  # noqa: E712

    @classmethod
    def get_or_none(cls, *query, **filters) -> 'FriendRequest':  # 增加类型提示
        return super().get_or_none(*query, **filters)

    @classmethod
    def get_one_not_finish(cls, uuid: str) -> Optional['FriendRequest']:
        """获取一个未完成的好友申请"""
        return cls.get_or_none(cls.uuid == uuid, cls.is_finish == False)  # noqa: E712
