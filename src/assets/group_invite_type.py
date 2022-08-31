from enum import Enum


class GroupInviteType(Enum):
    """群邀请类型"""
    ADD = 'add'  # 有人加群
    INVITE = 'invite'  # 有人邀请机器人加群
