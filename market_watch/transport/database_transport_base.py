import abc
from typing import List, Optional
from ..models import Product, User, ProductRef


class DatabaseTransport(abc.ABC):
    @abc.abstractmethod
    def get_all_subscribed_products(self) -> List[Product]:
        pass

    @abc.abstractmethod
    def get_products_by_refs(
        self,
        product_refs: List[ProductRef]
    ) -> List[Product]:
        pass

    @abc.abstractmethod
    def save_products(self, products: List[Product]):
        pass

    @abc.abstractmethod
    def get_user(self, id: str) -> Optional[User]:
        pass

    @abc.abstractmethod
    def get_subscribed_users(
        self,
        product_refs: List[ProductRef]
    ) -> List[User]:
        pass

    @abc.abstractmethod
    def save_user(self, user: User):
        pass
