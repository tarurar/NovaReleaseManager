"""
Nova release component module
"""
from typing import Optional
from .nova_status import Status
from .nova_component import NovaComponent


def get_release_status(component_statuses: list) -> Status:
    """Get release status"""
    if not component_statuses:
        return Status.UNDEFINED
    return min(component_statuses)


class NovaRelease:
    """Nova release component, readonly model"""

    def __init__(self, project, version, delivery):
        self.__version = version
        self.__delivery = delivery
        self.__project = project
        self.__components: list[NovaComponent] = []

    def __str__(self):
        return "Nova " + str(self.version) + ". Delivery " + str(self.delivery)

    def __repr__(self):
        return self.__str__()

    def __iter__(self):
        return iter(self.__components)

    @property
    def version(self):
        """Returns release version"""
        return self.__version

    @property
    def delivery(self):
        """Returns release delivery"""
        return self.__delivery

    @property
    def project(self):
        """Returns release project"""
        return self.__project

    @property
    def title(self) -> str:
        """Returns release title"""
        return str(self)

    def add_component(self, component: NovaComponent):
        """Adds component to release model"""
        self.__components.append(component)

    def get_status(self) -> Status:
        """Returns release status"""
        statuses = list({component.status for component in self.__components})
        return get_release_status(statuses)

    def describe_status(self) -> str:
        """Returns release status description"""
        text = [str(self), "*" * len(str(self))]
        for component in self.__components:
            text.append(component.describe_status())
        text.append("*" * len(str(self)))
        text.append("Total: " + str(len(self.__components)) + " component(s)")
        text.append(
            "Total: "
            + str(sum(len(component.tasks) for component in self.__components))
            + " task(s)"
        )
        text.append("Status: " + str(self.get_status()))
        return "\n".join(text)

    def get_component_by_name(self, name: str) -> Optional[NovaComponent]:
        """Returns component by name

        :param str name: Component name. If name ends with '!' then search
            will use strict equality, otherwise it will use 'in' operator.
            In any case search is case insensitive.
        """
        if name.endswith("!"):
            name = name[:-1]
            if not name:
                return None
            target_components = [
                c for c in self.__components if name.lower() == c.name.lower()
            ]
        else:
            target_components = [
                c for c in self.__components if name.lower() in c.name.lower()
            ]
        if not target_components:
            return None
        if len(target_components) > 1:
            raise ValueError("More than one component with same name found")
        return target_components[0]

    def can_release_version(self) -> bool:
        """Returns True if version can be released"""
        return self.get_status() == Status.DONE
