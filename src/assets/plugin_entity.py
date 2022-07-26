from assets.simple_plugin import SimplePlugin


class Plugin:
    def __init__(self, obj: SimplePlugin):
        self.obj: SimplePlugin = obj
        self.class_name = obj.__class__.__name__
        self.name = ''
        self.description = ''
        self.version = ''
        self.enable = False
