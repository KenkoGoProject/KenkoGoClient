

from rich.console import Console as RichConsole
from rich.pretty import pprint as pretty_print

from module.singleton_type import SingletonType


class Console(RichConsole, metaclass=SingletonType):

    @staticmethod
    def print_object(_object) -> None:
        """打印对象

        :param _object: 欲打印对象
        """
        pretty_print(_object, expand_all=True)


if __name__ == '__main__':
    console = Console()
