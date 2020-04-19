import abc
from typing import List
from ..models import ProductRef


class MessageQueue(abc.ABC):
    @abc.abstractmethod
    def enqueue(self, message_queue_items: List[ProductRef]):
        pass

    @abc.abstractclassmethod
    def deserialize(self, d: dict) -> List[ProductRef]:
        pass
