"""
This module contains the class NovaTagList,
which is a list of TagReference objects under the hood.
The list is associated with a NovaComponent object.
"""

from __future__ import annotations
from git import TagReference

from core.nova_component import NovaComponent
from core.nova_component_type import NovaComponentType
from integration.git import GitIntegration
import mappers


class NovaTagList:
    """
    List of TagReference objects. Essetially filters
    the tags that are relevant to the associated component
    starting from a given date.
    """

    def __init__(self, component: NovaComponent, since: str):
        self._component: NovaComponent = component
        self._since: str = since
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

    def filter(self, tag_template: str) -> NovaTagList:
        """
        Filter the list of tags by the given tag template.
        """
        filter_value = tag_template.lower()
        result = NovaTagList(self._component, self._since)
        for tag in self._list:
            if filter_value in tag.name.lower():
                result.try_add_tag(tag)

        return result

    @staticmethod
    def from_component(
        component: NovaComponent, since: str, git_integration: GitIntegration
    ) -> NovaTagList:
        """
        Create a new instance of NovaTagList for the given component
        starting from a given date.
        It essentially maps the NovaComponent to a NovaTagList.
        """
        if component.repo is None:
            return NovaTagList(component, since)

        all_tags = git_integration.list_tags(component.repo.url, since)
        result = NovaTagList(component, since)
        for tag in all_tags:
            result.try_add_tag(tag)

        return result
