from .product_status import ProductStatus
from .product_ref import ProductRef


class Product:
    def __init__(self, product_ref: ProductRef):
        self.product_ref = product_ref
        self.name = ""
        self.status = ProductStatus.UNKNOWN

    @property
    def platform(self):
        return self.product_ref.platform

    @property
    def id(self):
        return self.product_ref.id

    @classmethod
    def from_dict(cls, d: dict):
        p = cls(ProductRef.from_dict(d["_id"]))
        p.status = ProductStatus(d.get("status", "UNKNOWN"))
        p.name = d["name"]
        return p

    def __eq__(self, other: object):
        if isinstance(other, Product):
            return self.product_ref == other.product_ref
        return NotImplemented

    def to_dict(self) -> dict:
        return {
            "_id": self.product_ref.to_dict(),
            "name": self.name,
            "status": self.status.value
        }
