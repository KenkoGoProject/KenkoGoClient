# 插件概念

如果你使用过 CoolQ 系列并且有一定的 Python 基础，那么你可以很容易上手这章内容。
KenkoGoClient 是一个基础框架，只提供了连接到 KenkoGoServer 的功能，大多数与 QQ 交互的功能都要使用插件实现。

KenkoGoClient提供了一套简单的插件管理机制，你可以专注于你的功能实现，而不需要关心插件的管理。

## 目录结构

源码根目录下有一个 `plugin` 目录，你需要把所有插件放置于此处。

你也许注意到了，此处已带有一个 `hello_world_kenko.py` 的模块，这就是一个插件，
插件名必须以 `_kenko` 结尾，可以是模块或者是软件包。

## 让我们开始编写插件吧！

打开这个 `hello_world_kenko.py` 模块，可以发现里面有一个类 `HelloWorld`，
注意类名一定要与文件名中的 `hello_world` 相对应，并且类名使用大驼峰命名，即所有单词的首字母都要大写。

以上命名方法显然不符合一些命名规范，所以我们正在计划自定义类名，敬请期待。

```python
from assets.simple_plugin import SimplePlugin
class HelloWorld(SimplePlugin):
    PLUGIN_NAME = '你好，世界！'  # 插件名称
    PLUGIN_DESCRIPTION = '这是一个插件示例'  # 插件描述
    PLUGIN_VERSION = '1.0.0'  # 插件版本

    PLUGIN_DESCRIPTION_LONG = PLUGIN_DESCRIPTION  # 长描述，用于插件详情页
    PLUGIN_AUTHOR = 'AkagiYui'  # 插件作者
    PLUGIN_HELP_TEXT = '当有人@机器人时，机器人会让你想想'  # 插件帮助文本
    PLUGIN_LINK = 'https://akagiyui.com'  # 插件链接
```

你需要继承 `SimplePlugin` 类，以获取一些插件功能，如API。
`SimplePlugin` 类是插件模板， 该模板不实现功能。

你需要编写插件的基本信息，
至少需要定义 `PLUGIN_NAME`、`PLUGIN_DESCRIPTION`和`PLUGIN_VERSION` 属性，
否则插件将不会被加载。

---

```python
def __init__(self, *args, **kwargs):
    super().__init__(*args, **kwargs)
```

在 `__init__` 方法中，你可以做一些初始化工作，比如引入一些依赖，或设定一些全局变量。

注意：该方法不是必须的，如果你需要重写此方法，请务必调用 `super().__init__(*args, **kwargs)`，该父类方法提供了一些API。

1. 成员属性 `api` 暴露了所有已经封装好的 go-cqhttp 的 API，你可以用其实现`发送消息`等功能；
2. 成员属性 `client` 暴露了所有可以对 KenkoGoClient 进行的操作，如 `输出日志`；
3. 成员属性 `server` 暴露了所有可以对 KenkoGoServer 进行的操作，如 `获取 go-cqhttp 崩溃次数`。
4. 成员属性 `logger` 提供了`KenkoGoClient`的日志输出方法。

---

```python
from assets.cq_code import CqCode

def on_message(self, message: dict) -> bool:
    if message['post_type'] == 'message':
        msg: str = message['raw_message']
        if CqCode.at(message['self_id']) in msg:
            self.logger.info('有人叫我')
            message['message'] = '我希望你把篮球和鸡联系起来想想'
            self.api.send_msg(message)
    return True  # 返回True表示消息将被传递给下一个插件，返回False表示消息被拦截
```

当收到了来自 `go-cqhttp` 的消息时，`on_message` 方法会被调用。
参数 `message` 是一个 dict 实例，包含了消息的全部内容。
具体说明请参考[事件](https://docs.go-cqhttp.org/event/#%E9%80%9A%E7%94%A8%E6%95%B0%E6%8D%AE)。

你可以启动 KenkoGoServer 与 KenkoGoClient ，然后在一个 QQ 群 `@你的机器人`，机器人会发出一条消息。

注意该方法的返回值，如果为 `True`，则该消息将会被传递给下一个插件继续处理，否则将被**拦截**，不再处理。

---

如果你还有其他的需求，可以继续阅读下面的内容

---

```python
def on_enable(self):
    self.logger.info('HelloWorld enabled')
    return self
```

当插件被启用时，`on_enable` 方法会被调用，你可以在此进行数据库连接等操作。
请务必返回 `self`，否则将导致异常。

---

```python
def on_before_disable(self):
    self.logger.info('HelloWorld will be disabled')
    return self
```

当插件将被禁用时，`on_before_disable` 方法会被调用，你可以在此进行一些通知操作。
请务必返回 `self`，否则将导致异常。

---

```python
def on_disable(self):
    self.logger.info('HelloWorld disabled')
    return self
```

当插件被禁用时，`on_disable` 方法会被调用，你可以在此进行资源清理等操作。
请务必返回 `self`，否则将导致异常。

---

```python
def on_connect(self):
    self.logger.info('server connected')
    return self
```

当 KenkoGoServer 的 Websocket 连接成功时，`on_connect` 方法会被调用。
请务必返回 `self`，否则将导致异常。

---

```python
def on_disconnect(self):
    self.logger.info('server disconnected')
    return self
```

当断开与 KenkoGoServer 的 Websocket 连接时，`on_disconnect` 方法会被调用。
请务必返回 `self`，否则将导致异常。
