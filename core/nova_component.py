"""
Nova component module
"""

from core.nova_task import NovaTask

from .cvs import CodeRepository
from .nova_status import Status


def get_release_notes_md(
        revision_from: str,
        revision_to: str,
        repo_url: str,
        tasks: list[NovaTask]) -> str:
    """Returns release notes for component tasks in markdown format"""
    header = '## What\'s changed'

    task_notes = [('* ' + task.get_release_notes()) for task in tasks]

    change_log_url = get_changelog_url(revision_from, revision_to, repo_url)
    # change log is optional
    if change_log_url:
        change_log = f'**Full change log**: {change_log_url}'
    else:
        change_log = ''

    result = [header, *task_notes, '\n', change_log]

    return '\n'.join(result)


def get_changelog_url(
        revision_from: str,
        revision_to: str,
        repo_url: str) -> str:
    """Returns changelog url
    Revision from should be less than revision to
    GitHub format: https://github.com/LykkeBusiness/MT/compare/v2.20.2...v2.21.1
    """
    if revision_from is None or revision_to is None or repo_url is None:
        return ''

    revision_from = revision_from.strip().lower()
    revision_to = revision_to.strip().lower()
    repo_url = repo_url.strip().lower().rstrip('/')

    if not revision_from or not revision_to:
        return ''
    if not repo_url:
        return ''
    if revision_from >= revision_to:
        return ''

    result = f'{repo_url}/compare/{revision_from}...{revision_to}'
    return result


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

    def add_tasks(self, tasks):
        """Adds tasks to component"""
        self.tasks.extend(tasks)

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
        description = f'{self._name:<{width}}' + \
            f' | {str(status):<20}' + \
            f' | {tasks_count:>3} tasks'
        return description

    def get_release_notes(self, revision_from, revision_to) -> str:
        """Returns release notes for component"""
        return get_release_notes_md(
            revision_from,
            revision_to,
            self.repo.url,
            self.tasks)


class NovaEmptyComponent(NovaComponent):
    """
    Represents empty Nova component.
    It is used to group tasks only. According to convention it is
    named 'N/A' or 'n/a' in Jira.
    """

    default_component_name = 'n/a'
    component_names = [default_component_name, 'multiple components']

    def __init__(self):
        super().__init__(NovaEmptyComponent.default_component_name, None)

    @classmethod
    def parse(cls, component_name: str):
        """Parses component name"""
        normalized = component_name.strip().lower()
        if normalized in NovaEmptyComponent.component_names:
            return NovaEmptyComponent()
        return None
