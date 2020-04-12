import abc
from typing import List
from ..models import ProductRef


class MessageQueue(abc.ABC):
    @abc.abstractmethod
    def notify_updates(self, product_refs: List[ProductRef]):
        pass
