from dataclasses import dataclass


@dataclass
class SendMsgResult:
    message_id: int  # 消息 ID
