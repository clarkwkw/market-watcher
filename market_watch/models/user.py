from typing import List, Optional
from .product import ProductRef


class User:
    def __init__(
        self,
        chat_id: str,
        doc_id: Optional[str] = None,
        subscribed: List[ProductRef] = []
    ):
        self.chat_id = chat_id
        self.doc_id = doc_id
        self.subscribed = subscribed

    @classmethod
    def from_dict(cls, d: dict):
        subscribed = [ProductRef.from_dict(pr)
                      for pr in d.get("subscribed", [])]
        return cls(d["chat_id"], d.get("_id", None), subscribed=subscribed)

    def to_dict(self) -> dict:
        return {
            'chat_id': self.chat_id,
            'subscribed': [p.to_dict() for p in self.subscribed]
        }
