from dataclasses import dataclass


@dataclass
class StrangerInfo:
    user_id: int  # QQ 号
    nickname: str  # 昵称
    sex: str  # 性别 male female unknown
    age: int  # 年龄
    qid: str  # qid ID身份卡
    level: int  # 等级
    login_days: int  # 等级
