from dataclasses import dataclass


@dataclass
class LoginInfo:
    user_id: int  # 自身 QQ 号
    nickname: str  # 自身昵称
