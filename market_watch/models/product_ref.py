from .platform import Platform


class ProductRef:
    def __init__(self, platform: Platform, id: str):
        self.platform = Platform(platform)
        self.id = id

    @classmethod
    def from_dict(cls, d: dict):
        return cls(d["platform"], d["id"])

    def __eq__(self, other: object):
        if isinstance(other, ProductRef):
            return self.platform == other.platform and self.id == other.id
        return NotImplemented

    def __str__(self):
        return f"{self.platform}-{self.id}"

    def __hash__(self):
        return hash((self.platform, self.id))

    def to_dict(self):
        return {
            "platform": self.platform.value,
            "id": self.id
        }
