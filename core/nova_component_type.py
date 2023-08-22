"""
Nova component type enum
"""

from enum import IntEnum


class NovaComponentType(IntEnum):
    """Nova component type enum"""

    UNDEFINED = 0
    """Micro-service"""
    SERVICE = 1

    """Client/Contracts nuget package"""
    PACKAGE = 2

    """Infrastructure library nuget package"""
    PACKAGE_LIBRARY = 3

    def __str__(self):
        return self.name

    def __repr__(self):
        return self.__str__()
