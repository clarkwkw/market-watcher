import enum


class ProductStatus(enum.Enum):
    UNKNOWN = "UNKNOWN"
    AVAILABLE = "AVAILABLE"
    UNAVAILABLE = "UNAVAILABLE"
    NOT_FOUND = "NOT_FOUND"

    def __eq__(self, other: object):
        if isinstance(other, ProductStatus):
            return self.value == other.value
        elif isinstance(other, str):
            return self.value.upper() == other.upper()
        return NotImplemented
