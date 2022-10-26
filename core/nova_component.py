"""
Nova component module
"""

from .cvs import CodeRepository
from .nova_status import Status


class NovaComponent:
    """
    Represents Nova component registered in Jira
    """
    longest_component_name = 0

    def __init__(self, name: str, repo: CodeRepository):
        self._name = name
        self.tasks = []
        self.repo = repo
        if len(self._name) > NovaComponent.longest_component_name:
            NovaComponent.longest_component_name = len(self._name)

    def __str__(self):
        return self._name

    def __repr__(self):
        return self.__str__()

    def __eq__(self, other):
        return self._name == other.name

    @property
    def name(self):
        """Component name"""
        return self._name

    def add_task(self, task):
        """Adds task to component"""
        self.tasks.append(task)

    def get_status(self):
        """Returns component status"""
        if not self.tasks:
            return Status.UNDEFINED
        statuses = [task.status for task in self.tasks]
        if any(s == Status.UNDEFINED for s in statuses):
            return Status.UNDEFINED
        if all(s == Status.READY_FOR_RELEASE for s in statuses):
            return Status.READY_FOR_RELEASE
        if all(s == Status.DONE for s in statuses):
            return Status.DONE
        return Status.IN_DEVELOPMENT

    def describe_status(self) -> str:
        """Returns component status description"""
        status = self.get_status()
        tasks_count = len(self.tasks)
        width = NovaComponent.longest_component_name
        return f'{self._name:<{width}} | {str(status):<15} | {tasks_count:>3} tasks'

    def get_release_notes(self) -> str:
        """Returns release notes for component"""
        return 'Release notes'
