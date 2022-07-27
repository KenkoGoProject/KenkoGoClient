from typing import List

from rich.console import Console as RichConsole
from rich.pretty import pprint as pretty_print
from rich.prompt import Confirm, Prompt

from module.singleton_type import SingletonType


class Console(RichConsole, metaclass=SingletonType):
    @staticmethod
    def ask(*args, **kwargs):
        return Confirm.ask(*args, **kwargs)

    @staticmethod
    def pretty_print(_object, **kwargs):
        pretty_print(_object, expand_all=True, **kwargs)

    @staticmethod
    def choose(prompt: str, choices: List[str], default: str = None, *args, **kwargs):
        return Prompt.ask(prompt=prompt, choices=choices, default=default, *args, **kwargs)


if __name__ == '__main__':
    console = Console()
    print(console.choose(prompt='选择插件', choices=['a1', 'b2', 'c3']))
