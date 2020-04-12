import enum
from typing import Union


class Language(enum.Enum):
    EN = "EN"

    def __eq__(self, other: Union[str, 'Language']):
        if type(other) == 'Language':
            return self.value == other.value
        return self.value == other

    def __hash__(self):
        return hash(self.value)
