from assets.simple_plugin import SimplePlugin


class Plugin:
    """插件类"""

    def __init__(self, obj: SimplePlugin):
        self.obj: SimplePlugin = obj
        self.class_name = obj.__class__.__name__
        self.name = obj.name
        self.description = obj.description
        self.version = obj.version
        self.enable = False
