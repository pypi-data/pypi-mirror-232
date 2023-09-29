from enum import Enum


class BaseEnum(Enum):

    def __get__(self, instance, owner):
        return self.value
