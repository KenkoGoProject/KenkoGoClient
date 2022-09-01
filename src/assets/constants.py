APP_NAME = 'KenkoGoClient'  # 应用名称
AUTHOR_NAME = 'AkagiYui'  # 作者
VERSION_NUM = 21  # 版本号
VERSION_STR = '0.4.6'  # 版本名称
APP_DESCRIPTION = 'A simple client of KenkoGoServer'  # 描述


ADMIN_HELP_TEXT = 'ADMIN_HELP_TEXT', f"""超级管理员操作菜单：
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

HELP_TEXT = 'HELP_TEXT', """操作菜单：
[CP]help - 显示帮助信息（即本信息）
[CP]? - 同上"""

INVITE_HELP_TEXT = 'INVITE_HELP_TEXT', """

忽略发送：[CP]0 [UUID]
同意发送：[CP]1 [UUID]
拒绝发送：[CP]2 [UUID]"""
