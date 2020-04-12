import enum
from typing import Union


class ProductStatus(enum.Enum):
    UNKNOWN = "UNKNOWN"
    AVAILABLE = "AVAILABLE"
    UNAVAILABLE = "UNAVAILABLE"
    NOT_FOUND = "NOT_FOUND"

    def __eq__(self, other: Union[str, 'ProductStatus']):
        if type(other) == 'ProductStatus':
            return self.value == other.value
        return self.value == other
