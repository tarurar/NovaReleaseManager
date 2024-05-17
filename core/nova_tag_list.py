"""
This module contains the class NovaTagList,
which is a list of TagReference objects under the hood.
The list is associated with a NovaComponent object.
"""

from __future__ import annotations
from typing import Sequence
from git import TagReference

from core.nova_component import NovaComponent
from core.nova_component_type import NovaComponentType
import mappers


class NovaTagList:
    """
    List of TagReference objects
    """

    def __init__(self, component: NovaComponent):
        self._component: NovaComponent = component
        self._list: list[TagReference] = []

    def __iter__(self):
        return iter(self._list)

    def __len__(self):
        return len(self._list)

    @property
    def component(self) -> NovaComponent:
        """
        Returns associated component
        """
        return self._component

    def try_add_tag(self, tag: TagReference) -> bool:
        """
        Try to add tag to the list if only it matches the
        component and if only it is not already in the list

        :param tag: Tag to add
        :return: True if tag was added, False otherwise
        """
        if tag in self._list:
            return False

        match self._component.ctype:
            case NovaComponentType.SERVICE:
                if mappers.is_service_tag(self._component, tag):
                    self._list.append(tag)
                    return True
            case NovaComponentType.PACKAGE | NovaComponentType.PACKAGE_LIBRARY:
                if mappers.is_package_tag(self._component, tag):
                    self._list.append(tag)
                    return True
            case _:
                self._list.append(tag)
                return True

        return False

    @staticmethod
    def from_list(
        component: NovaComponent, tags: Sequence[TagReference]
    ) -> NovaTagList:
        """
        Create a new instance of NovaTagList from the list of tags
        """
        result = NovaTagList(component)
        for tag in tags:
            result.try_add_tag(tag)

        return result
