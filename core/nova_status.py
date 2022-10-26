"""
Nova status module
"""
from enum import Enum


class Status(Enum):
    """Nova status enum"""
    IN_DEVELOPMENT = 1
    READY_FOR_RELEASE = 2
    DONE = 3
    UNDEFINED = 4

    def __str__(self):
        return self.name

    def __repr__(self):
        return self.__str__()
