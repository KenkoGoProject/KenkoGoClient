class SimplePlugin:
    def __init__(self):
        """实例初始化
        不建议在此处做任何操作，因为这个函数会在插件加载时被调用
        """
        print('Initializing SimplePlugin...')

    def on_enable(self):
        print('plugin enabled')
        # return False  # not enabled
        return True  # enabled

    def on_before_disable(self):
        print('before disable')

    def on_disable(self):
        print('plugin disabled')

    def on_connect(self):
        print('server connected')

    def on_message(self, message: dict):
        print(f'message received {message}')

    def on_disconnect(self):
        print('server disconnected')
