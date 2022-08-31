from peewee import Model


class BaseModel(Model):
    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        self.UUIDS = self._meta.database.UUIDS
