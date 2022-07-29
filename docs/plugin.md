# 插件概念

如果你使用过 CoolQ 系列并且有一定的 Python 基础，那么你可以很容易上手这章内容。
KenkoGoClient 是一个基础框架，只提供了连接到 KenkoGoServer 的功能，一切与 QQ 交互的功能都要使用插件实现。

KenkoGoClient提供了一套简单的插件管理机制，你可以专注于你的功能实现，而不需要关心插件的管理。

## 编写插件

源码根目录下有一个 `plugin` 目录，你需要把所有插件放置于此处。

你也许注意到了，此处已带有一个 `hello_world_kenko.py` 的模块，这就是一个插件，
插件名必须以 `_kenko` 结尾，可以是模块或者是软件包。

---

打开这个 `hello_world_kenko.py` 模块，可以发现里面有一个类 `HelloWorld`，
注意类名一定要与文件名中的 `hello_world` 相对应，并且类名使用大驼峰命名，即所有单词的首字母都要大写。

```python
from assets.simple_plugin import SimplePlugin
class HelloWorld(SimplePlugin):
    ...
```

一般情况下，你可以继承 `SimplePlugin` 类，以达到省略部分方法的目的。
`SimplePlugin` 类是插件模板， 该模板不实现任何功能，
但是它提供了一些必要的属性和方法，以防止再触发事件时引发异常。

---

```python
from module.gocq_api import GocqApi
from module.client_api import ClientApi
from module.server_api import ServerApi

def __init__(self, api: GocqApi, client: ClientApi, server: ServerApi):
    super().__init__(api, client, server)
    self.api = api
    self.client = client
    self.server = server
    self.name = '你好，世界！'
    self.description = '这是一个插件示例'
    self.version = '1.0.0'
```

在 `__init__` 方法中，定义了一些实例属性，你需要在这里填写你的插件信息，
如：插件名、描述、版本。
该方法中**强烈建议不要**进行其他任何操作！

该方法是**必须**的，否则插件将不会被加载，并且该方法会在 KenkoGoClient 启动时被调用。

其中，
参数 `api` 暴露了所有已经封装好的 go-cqhttp 的 API，你可以用其实现`发送消息`等功能；
参数 `client` 暴露了所有可以对 KenkoGoClient 进行的操作，如 `输出日志`；
参数 `server` 暴露了所有可以对 KenkoGoServer 进行的操作，如 `获取 go-cqhttp 崩溃次数`。

---

```python
from assets.cq_code import CqCode

def on_message(self, message: dict) -> bool:
    print('received message:', message)
    if message['post_type'] == 'message':
        msg: str = message['raw_message']
        if CqCode.at(message['self_id']) in msg:
            print('有人叫我')
            message['message'] = '你干嘛~~~哈哈~~哎哟~~'
            self.api.send_msg(message)
    return True
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
def on_initialize(self):
    print('Initializing HelloWorld...')
    return self
```

在 `on_initialize` 方法中，你可以做一些初始化工作，比如引入一些依赖，或设定一些全局变量。

请务必返回 `self`，否则将导致异常，并且该方法会在 KenkoGoClient 启动时被调用。

---

```python
def on_enable(self):
    print('HelloWorld enabled')
    return self
```

当插件被启用时，`on_enable` 方法会被调用，你可以在此进行数据库连接等操作。
请务必返回 `self`，否则将导致异常。

---

```python
def on_before_disable(self):
    print('HelloWorld will be disabled')
    return self
```

当插件将被禁用时，`on_before_disable` 方法会被调用，你可以在此进行一些通知操作。
请务必返回 `self`，否则将导致异常。

---

```python
def on_disable(self):
    print('HelloWorld disabled')
    return self
```

当插件被禁用时，`on_disable` 方法会被调用，你可以在此进行资源清理等操作。
请务必返回 `self`，否则将导致异常。

---

```python
def on_connect(self):
    print('server connected')
    return self
```

当 KenkoGoServer 的 Websocket 连接成功时，`on_connect` 方法会被调用。
请务必返回 `self`，否则将导致异常。

---

```python
def on_disconnect(self):
    print('server disconnected')
    return self
```

当断开与 KenkoGoServer 的 Websocket 连接时，`on_disconnect` 方法会被调用。
请务必返回 `self`，否则将导致异常。
