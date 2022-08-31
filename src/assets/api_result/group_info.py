from dataclasses import dataclass


@dataclass
class GroupInfo:
    """如果机器人尚未加入群, group_create_time, group_level, max_member_count 和 member_count 将会为0"""
    group_id: int  # 群号
    group_name: str  # 群名
    group_memo: str  # 群备注
    group_create_time: int  # 群创建时间
    group_level: int  # 群等级
    member_count: int  # 群成员数
    max_member_count: int  # 群最大成员数
