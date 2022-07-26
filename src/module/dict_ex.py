from collections import UserDict


class DictEx(UserDict):
    """
    增强字典类
    1. 键用半角实心点.做下级入口
    例  原 dict['web']['port'] 现 Utils.Dict['web.port']
    """
    def __init__(self, ignore_key_error: bool = True, *args, **kwargs):
        super().__init__(*args, **kwargs)
        self.ignore_key_error = ignore_key_error

    def __contains__(self, ori_keys: str):    # type: ignore[override]
        now_dict: UserDict = super()  # type: ignore[assignment]
        for key in ori_keys.split('.'):
            try:
                now_dict = now_dict.__getitem__(key)
            except KeyError:
                return False
        return True

    def __getitem__(self, ori_keys: str):
        now_dict: UserDict = super()  # type: ignore[assignment]
        for key in ori_keys.split('.'):
            try:
                now_dict = now_dict.__getitem__(key)
            except KeyError:
                if self.ignore_key_error:
                    return None
                else:
                    raise
        return now_dict

    def __setitem__(self, ori_key: str, ori_value):
        keys: list[str] = ori_key.split('.')
        now_dict: UserDict = super()  # type: ignore[assignment]
        for key in keys[:-1]:
            if not now_dict.__contains__(key):
                now_dict.__setitem__(key, {})
            now_dict = now_dict.__getitem__(key)
        now_dict.__setitem__(keys[-1], ori_value)


if __name__ == '__main__':
    d = DictEx()
    print(d)
    print(d['ws.port'])
    d['ws.port'] = 8080
    print(d)
    print(d['ws.port'])
    print(d['ws']['port'])
    d['http']['port'] = 3000  # not support
    print(d)
    print(d['http.port'])
    print(d['http']['port'])
