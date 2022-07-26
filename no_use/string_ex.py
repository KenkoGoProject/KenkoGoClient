from collections import UserString
from typing import Generator, Iterable, Union


class StrEx(UserString):
    """
    增强字符串类
    重载in支持判断列表或元组成员是否出现在字符串里
    重写find()、startswith()支持查找子串列表、元组或集合
    新增replace_all()方法支持替换所有匹配的子串
    """

    def __contains__(self, item) -> bool:
        if isinstance(item, str):
            return super().__contains__(item)
        elif isinstance(item, Iterable):
            return any((True for i in item if i in self))
        raise TypeError(f"'in' operator not supported for type '{type(item)}'")

    def find(self, __sub: Iterable, __start=None, __end=None) -> Union[int, Generator]:  # type: ignore[override]
        if isinstance(__sub, str):
            return super().find(__sub, __start, __end)
        elif isinstance(__sub, Iterable):
            return (super(self.__class__, self).find(i, __start, __end) for i in __sub)
        raise TypeError(f"find() argument must be a string or iterable, not '{type(__sub)}'")

    def startswith(self, __prefix: Iterable, __start=None, __end=None) -> bool:
        if isinstance(__prefix, str):
            return super().startswith(__prefix, __start, __end)
        if isinstance(__prefix, Iterable):
            return any(super(self.__class__, self).startswith(i, __start, __end) for i in __prefix)
        raise TypeError(f"startswith() argument must be a string or iterable, not '{type(__prefix)}'")

    def replace_all(self, __old: str, __new: str):
        t = self
        while __old in t:
            t = t.replace(__old, __new)
        return t


if __name__ == '__main__':
    example_1 = StrEx('咱吃什么')
    example_2 = StrEx('吃什么东西')
    word_what_self = ('我', '俺', '咱', '我们')

    assert '东西' not in example_1
    assert '东西' in example_2
    assert word_what_self in example_1
    assert word_what_self not in example_2
    assert example_1.find('什') == 2
    assert example_2.find('什') == 1
    assert list(example_1.find(word_what_self)) == [-1, -1, 0, -1]  # type: ignore[arg-type]
    assert list(example_2.find(word_what_self)) == [-1, -1, -1, -1]  # type: ignore[arg-type]
    assert example_1.startswith('咱')
    assert not example_2.startswith('咱')
    assert example_1.startswith(word_what_self)
    assert not example_2.startswith(word_what_self)
    assert StrEx('我这有\n\n\n三个换行').replace_all('\n\n', '\n') == '我这有\n三个换行'
