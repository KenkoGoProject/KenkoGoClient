import threading


class SingletonType(type):
    _instance_lock = threading.Lock()
    _instance = None

    def __call__(cls, *args, **kwargs):
        if not cls._instance:
            with cls._instance_lock:
                if not cls._instance:
                    cls._instance = super().__call__(*args, **kwargs)
        return cls._instance
