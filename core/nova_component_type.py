"""
Nova component type enum
"""

from enum import IntEnum


class NovaComponentType(IntEnum):
    """Nova component type enum"""

    UNDEFINED = 0
    SERVICE = 1
    PACKAGE = 2

    def __str__(self):
        return self.name

    def __repr__(self):
        return self.__str__()
