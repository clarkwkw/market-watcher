import enum


class Language(enum.Enum):
    EN = "EN"

    def __eq__(self, other: object):
        if isinstance(other, Language):
            return self.value == other.value
        elif isinstance(other, str):
            return self.value == other
        return NotImplemented

    def __hash__(self):
        return hash(self.value)
