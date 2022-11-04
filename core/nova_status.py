"""
Nova status module
"""
from enum import IntEnum


class Status(IntEnum):
    """Nova status enum"""
    UNDEFINED = 0
    IN_DEVELOPMENT = 1
    READY_FOR_RELEASE = 2
    DONE = 3

    def __str__(self):
        return self.name

    def __repr__(self):
        return self.__str__()
