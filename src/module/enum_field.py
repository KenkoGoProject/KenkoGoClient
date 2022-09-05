from enum import Enum
from typing import Any, Type

from peewee import IntegerField


class EnumField(IntegerField):
    """This class enable an Enum like field for Peewee"""

    def __init__(self, choices: Type[Enum], *args, **kwargs):
        super(IntegerField, self).__init__(*args, **kwargs)
        self.choices = choices

    def db_value(self, value: Enum) -> Any:
        return value.value

    def python_value(self, value: str) -> Enum:
        return self.choices(value)
