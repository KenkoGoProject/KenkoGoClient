APP_NAME = 'KenkoGoClient'  # 应用名称
APP_DESCRIPTION = 'A simple client of KenkoGoServer'  # 描述
AUTHOR_NAME = 'AkagiYui'  # 作者
VERSION_NUM = 23  # 版本号
VERSION_STR = '0.4.8'  # 版本名称

COMMAND_HELP_TEXT = """支持的命令 Available commands:
/help: 显示此帮助 Show this help message
/exit: 退出KenkoGoClient Quit the application

/connect: 连接Server Connect to the server
/disconnect: 断开连接 Disconnect from the server

/info: 查看Client状态 Show the client status
/status: 查看Server状态 Show the server status

/start: 启动go-cqhttp Start go-cqhttp
/stop: 停止go-cqhttp Stop go-cqhttp
/qrcode: 显示登录二维码 Show qrcode of go-cqhttp

/list：列出插件信息 List plugins
/reload <name>: 重载插件 Reload plugins
/enable <name>: 启用插件 Enable plugin
/disable <name>: 禁用插件 Disable plugin
/up <name>: 上移插件 Move plugin up
/down <name>: 下移插件 Move plugin down
"""

ADMIN_HELP_TEXT = f"""超级管理员操作菜单：
当前版本({VERSION_STR})支持的命令：
[CP]h - 显示本信息
[CP]help - 显示帮助信息（非超级管理员特有）
[CP]status - 显示当前状态
[CP]screen - 截屏
[CP]set - 查看设置
[CP]ls - 列出白名单/黑名单
[CP]? - 判断群是否在白名单中
[CP]add - 将本群加入白名单
[CP]del - 将本群从白名单移除

[CP]todo - 查看待办事项（如好友请求、群聊邀请）
[CP]1 <id> - 同意请求
[CP]0 <id> - 拒绝请求

--[CP]add u <QQ号> - 将QQ号加入白名单
--[CP]add g <群号> - 将群加入白名单
--[CP]del u <QQ号> - 将QQ号从白名单移除
--[CP]del g <群号> - 将群从白名单移除"""

HELP_TEXT = """操作菜单：
[CP]help - 显示帮助信息（即本信息）
[CP]? - 同上"""

INVITE_HELP_TEXT = """

忽略发送：[CP]0 [UUID]
同意发送：[CP]1 [UUID]
拒绝发送：[CP]2 [UUID]"""
