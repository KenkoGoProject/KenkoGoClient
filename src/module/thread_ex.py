import ctypes
import inspect
import threading


class ThreadEx(threading.Thread):
    """增强线程类，支持结束线程"""

    def kill(self):
        exctype = SystemExit
        # raises the exception, performs cleanup if needed
        tid = ctypes.c_long(self.ident)
        if not inspect.isclass(exctype):
            exctype = type(exctype)
        res = ctypes.pythonapi.PyThreadState_SetAsyncExc(tid, ctypes.py_object(exctype))
        if res == 0:
            raise ValueError("invalid thread id")
        elif res != 1:
            # if it returns a number greater than one, you're in trouble,
            # and you should call it again with exc=NULL to revert the effect
            ctypes.pythonapi.PyThreadState_SetAsyncExc(tid, None)
            raise SystemError("PyThreadState_SetAsyncExc failed")


if __name__ == '__main__':
    import time

    def run_forever():
        while True:
            print('hello')
            time.sleep(0.1)

    example_1 = ThreadEx(target=run_forever)
    example_1.start()
    time.sleep(2)
    example_1.kill()
