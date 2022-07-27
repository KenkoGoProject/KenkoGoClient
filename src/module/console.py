from rich.console import Console as RichConsole
from rich.pretty import pprint as pretty_print
from rich.prompt import Confirm

from module.singleton_type import SingletonType


class Console(RichConsole, metaclass=SingletonType):
    @staticmethod
    def ask(*args, **kwargs):
        return Confirm.ask(*args, **kwargs)

    @staticmethod
    def pretty_print(_object, **kwargs):
        pretty_print(_object, expand_all=True, **kwargs)


if __name__ == '__main__':
    console = Console()
    console.ask('Are you sure?')
