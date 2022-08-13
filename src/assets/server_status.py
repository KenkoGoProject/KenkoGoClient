from dataclasses import dataclass


@dataclass
class ServerStatus:
    python_version: str
    system_description: str

    system_cpu_present: float
    system_memory_usage: float
    kenkogo_memory_usage: float

    system_uptime: str
    kenkogo_uptime: str

    instance_running: bool
    gocq_msg_count: int
