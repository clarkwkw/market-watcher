import enum


class Platform(enum.Enum):
    AMAZON_JP = "AMAZON_JP"

    @classmethod
    def is_valid(cls, value: str):
        values = set(item.value for item in Platform)
        return value in values
