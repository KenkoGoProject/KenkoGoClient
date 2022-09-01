from queue import PriorityQueue
from typing import Tuple

from assets.prioritized_item import PrioritizedItem


class MessageQueue(PriorityQueue):
    """消息队列"""

    def put(self, _type: str, message: dict = None, priority: int = 100):
        super().put(PrioritizedItem(priority, (_type, message)))

    # noinspection PyMethodOverriding
    def get(self) -> Tuple[str, dict]:
        item: PrioritizedItem = super().get()
        return item.item
