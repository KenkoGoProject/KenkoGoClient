from assets.simple_plugin import SimplePlugin


class GoodbyeWorld(SimplePlugin):
    """你可以在继承SimplePlugin的情况下只保留__init__方法"""

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        self.name = '再见，世界！'
        self.description = '插件也可以是一个包'
        self.version = '1.2.3'
