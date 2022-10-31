"""
Nova release component module
"""
from .nova_status import Status
from .nova_component import NovaComponent


class NovaRelease(object):
    """Nova release component"""

    def __init__(self, project, version, delivery):
        self.version = version
        self.delivery = delivery
        self.project = project
        self.components = []

    def __str__(self):
        return 'Nova ' + str(self.version) + ". Delivery " + str(self.delivery)

    def __repr__(self):
        return self.__str__()

    def get_title(self) -> str:
        """Returns release title"""
        return str(self)

    def add_component(self, component: NovaComponent):
        """Adds component to release"""
        self.components.append(component)

    def get_status(self):
        """Returns release status"""
        statuses = list(set([component.get_status()
                        for component in self.components]))
        if not statuses:
            return Status.UNDEFINED
        if any(s == Status.UNDEFINED for s in statuses):
            return Status.UNDEFINED
        if all(s == Status.READY_FOR_RELEASE for s in statuses):
            return Status.READY_FOR_RELEASE
        if all(s == Status.DONE for s in statuses):
            return Status.DONE
        if Status.READY_FOR_RELEASE in statuses and Status.DONE in statuses:
            return Status.READY_FOR_RELEASE
        return Status.IN_DEVELOPMENT

    def describe_status(self):
        """Returns release status description"""
        text = [str(self), '*' * len(str(self))]
        for component in self.components:
            text.append(component.describe_status())
        text.append('*' * len(str(self)))
        text.append('Total: ' + str(len(self.components)) + ' component(s)')
        text.append('Total: ' + str(sum([len(component.tasks)
                    for component in self.components])) + ' task(s)')
        text.append('Status: ' + str(self.get_status()))
        return '\n'.join(text)

    def get_component_by_name(self, name: str):
        """Returns component by name"""
        target_components = [
            c for c in self.components if name.lower() in c.name.lower()]
        if not target_components:
            return None
        if len(target_components) > 1:
            raise Exception('More than one component found')
        return target_components[0]
