from uuid import uuid4

from peewee import (SQL, BooleanField, CharField, DateTimeField, IntegerField,
                    Model)


class FriendRequest(Model):
    flag = CharField(primary_key=True)
    user_id = IntegerField()
    comment = CharField()
    finish = BooleanField(default=False)
    finish_by = IntegerField(null=True)
    uuid = CharField(null=True, unique=True)

    def __init__(self, *args, **kwargs):
        super(FriendRequest, self).__init__(*args, **kwargs)
        if not self.uuid:
            self.uuid = str(uuid4().int)[:7]

    created_at = DateTimeField(constraints=[SQL('DEFAULT CURRENT_TIMESTAMP')], null=True)
    updated_at = DateTimeField(constraints=[SQL('DEFAULT CURRENT_TIMESTAMP')], null=True)
    deleted_at = DateTimeField(null=True)

    class Meta:
        table_name = 'friend_request'

    # noinspection PyMethodOverriding
    def save(self, update=False):
        return super().save(not update)
