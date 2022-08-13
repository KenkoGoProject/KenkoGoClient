from dataclasses import dataclass


@dataclass
class ClientStatus:
    python_version: str
    system_description: str

    system_cpu_present: float
    system_memory_usage: float
    kenkogo_memory_usage: float

    system_uptime: str
    kenkogo_uptime: str

    connected: bool
    app_name: str
    version: str
    websocket_message_count: int
