import abc
from ..models import Product


class CrawlerBase(abc.ABC):
    @abc.abstractmethod
    def get_product(self,  id: str) -> Product:
        pass

    @abc.abstractclassmethod
    def get_product_url(cls, id: str) -> str:
        pass
