import json
import os

from module.atomicwrites import atomic_write
from module.singleton_type import SingletonType


class Internationalization(metaclass=SingletonType):
    def __init__(self, lang_path: str, default_lang: str, auto_load: bool = True):
        self.lang_path = lang_path
        self.lang_dict: dict[str, str] = {}
        self.default_lang = default_lang
        if auto_load:
            self.set_lang(default_lang)

    def _load_lang(self, lang: str) -> dict:
        try:
            with open(os.path.join(self.lang_path, f'{lang}.json'), encoding='utf-8') as f:
                return json.load(f)
        except FileNotFoundError:
            return {}

    def set_lang(self, lang: str):
        self.lang_dict = self._load_lang(lang)

    def get_text(self, key: str, lang: str = None):
        _dict = self.lang_dict if lang is None else self._load_lang(lang)
        try:
            return _dict[key]
        except KeyError:
            _dict[key] = key
            return key

    def save(self):
        with atomic_write(os.path.join(self.lang_path, f'{self.default_lang}.json'), overwrite=True, encoding='utf-8') as f:
            json.dump(self.lang_dict, f, indent=4, ensure_ascii=False)

    def __del__(self):
        self.save()
