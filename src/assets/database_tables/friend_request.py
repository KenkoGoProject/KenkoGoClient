from datetime import datetime
from typing import Optional
from uuid import uuid4

from peewee import CharField, IntegerField, Model
from playhouse.apsw_ext import BooleanField, DateTimeField


class FriendRequest(Model):
    flag: str = CharField(primary_key=True)
    user_id: int = IntegerField()
    comment: str = CharField()
    is_finish: bool = BooleanField(default=False)
    finish_by: int = IntegerField(null=True)
    finish_at: datetime = DateTimeField(null=True)
    uuid: Optional[str] = CharField(null=True, unique=True)

    def __init__(self, *args, **kwargs):
        super(FriendRequest, self).__init__(*args, **kwargs)
        while not self.uuid:
            uuid: str = str(uuid4().int)[:7]
            if not FriendRequest.get_or_none(FriendRequest.uuid == uuid):
                self.uuid = uuid

    created_at: datetime = DateTimeField(default=datetime.now, null=True)
    updated_at: datetime = DateTimeField(default=datetime.now, null=True)

    class Meta:
        table_name = 'friend_request'

    # noinspection PyMethodOverriding
    def save(self, update=False):
        if update:
            self.updated_at = datetime.now()
        return super().save(not update)

    def finish(self, user_id):
        """
        完成好友申请

        :param user_id: 完成者的QQ号
        :return: 影响的行数
        """
        self.is_finish = True
        self.finish_by = user_id
        self.uuid = None
        self.finish_at = datetime.now()
        return self.save(True)

    @classmethod
    def get_or_none(cls, *query, **filters) -> 'FriendRequest':  # 增加类型提示
        return super().get_or_none(*query, **filters)
