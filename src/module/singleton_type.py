class SingletonType(type):
    """单例模式"""

    _instance = None

    def __call__(cls, *args, **kwargs) -> object:
        # TODO: 线程安全
        if not cls._instance:
            cls._instance = super().__call__(*args, **kwargs)
        return cls._instance
