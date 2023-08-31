"""
Nova component module
"""

from packaging.version import parse
from core.nova_task import NovaTask
from git_utils import sanitize_git_url
from .cvs import CodeRepository, GitCloudService
from .nova_status import Status
from .nova_component_type import NovaComponentType


def compare_revisions(revision1: str, revision2: str) -> bool:
    """
    Compares two versions

    :param revision1: The first version to compare.
    :param revision2: The second version to compare.
    :return: True if version1 is less than version2, False otherwise.
    :raises: ValueError if version1 or version2 is None.
    :raises: InvalidVersion if version1 or version2 is invalid.
    """
    if revision1 is None:
        raise ValueError("Revision1 is None")
    if revision2 is None:
        raise ValueError("Revision2 is None")

    # cut beginning 'nova-' if exists
    revision1 = revision1[5:] if revision1.startswith("nova-") else revision1
    revision2 = revision2[5:] if revision2.startswith("nova-") else revision2

    parsed_revision1 = parse(revision1)
    parsed_revision2 = parse(revision2)

    return parsed_revision1 < parsed_revision2


def get_release_notes_github(
    revision_from: str, revision_to: str, repo_url: str, tasks: list[NovaTask]
) -> str:
    """Returns release notes for component tasks in markdown format"""
    header = "## What's changed"

    task_notes = [("* " + task.get_release_notes()) for task in tasks]

    change_log_url = get_changelog_url(revision_from, revision_to, repo_url)
    # change log is optional
    if change_log_url:
        change_log = f"**Full change log**: {change_log_url}"
    else:
        change_log = ""

    result = [header, *task_notes, "\n", change_log]

    return "\n".join(result)


def get_release_notes_bitbucket(tasks: list[NovaTask]) -> str:
    """Returns release notes for component tasks in markdown format"""
    task_notes = [("* " + task.get_release_notes()) for task in tasks]
    return "\n".join(task_notes)


def get_changelog_url(
    revision_from: str, revision_to: str, repo_url: str
) -> str:
    """
    Build change log url.

    :param revision_from: The revision from. Should be less than revision to.
    :param revision_to: The revision to. Should be greater than revision from.
    :param repo_url: The repository url.
    :return: The change log url. GitHub format:
        https://github.com/LykkeBusiness/MT/compare/v2.20.2...v2.21.1
    """
    if revision_from is None or revision_to is None or repo_url is None:
        return ""

    revision_from = revision_from.strip().lower()
    revision_to = revision_to.strip().lower()
    repo_url = repo_url.strip().lower().rstrip("/")
    repo_url = sanitize_git_url(repo_url)

    if not revision_from or not revision_to:
        return ""
    if not repo_url:
        return ""
    if not compare_revisions(revision_from, revision_to):
        return ""

    result = f"{repo_url}/compare/{revision_from}...{revision_to}"
    return result


def parse_component_type(name: str) -> NovaComponentType:
    """
    Parses component type from component name.
    By default it is a micro-service.

    :param name: The component name.
    :return: Component type.
    """
    if name is None or not name:
        return NovaComponentType.UNDEFINED

    normalized_name = name.lower()
    if normalized_name.endswith("contracts"):
        return NovaComponentType.PACKAGE
    if normalized_name.endswith("client"):
        return NovaComponentType.PACKAGE
    if normalized_name.endswith("library"):
        return NovaComponentType.PACKAGE_LIBRARY

    return NovaComponentType.SERVICE


class NovaComponent:
    """
    Represents Nova component registered in Jira
    """

    longest_component_name = 0

    def __init__(self, name: str, repo: CodeRepository | None):
        self.__name = name
        self.__ctype = parse_component_type(name)
        self.__tasks = []
        self.repo = repo
        if len(self.__name) > NovaComponent.longest_component_name:
            NovaComponent.longest_component_name = len(self.__name)

    def __str__(self):
        return self.__name

    def __repr__(self):
        return self.__str__()

    def __eq__(self, other):
        return self.__name == other.name

    @property
    def name(self):
        """Component name"""
        return self.__name

    @property
    def tasks(self) -> list[NovaTask]:
        """Returns component tasks"""
        return self.__tasks

    @property
    def ctype(self) -> NovaComponentType:
        """Returns component type"""
        return self.__ctype

    def add_task(self, task: NovaTask):
        """Adds task to component"""
        self.__tasks.append(task)

    def add_tasks(self, tasks: list[NovaTask]):
        """Adds tasks to component"""
        self.__tasks.extend(tasks)

    @property
    def status(self) -> Status:
        """Returns component status"""
        if not self.__tasks:
            return Status.UNDEFINED
        statuses = [task.status for task in self.__tasks]
        if any(s == Status.UNDEFINED for s in statuses):
            return Status.UNDEFINED
        if all(s == Status.DONE for s in statuses):
            return Status.DONE
        if all(s >= Status.READY_FOR_RELEASE for s in statuses):
            return Status.READY_FOR_RELEASE
        return Status.IN_DEVELOPMENT

    def describe_status(self) -> str:
        """Returns component status description"""
        tasks_count = len(self.__tasks)
        width = NovaComponent.longest_component_name
        description = (
            f"{self.__name:<{width}}"
            + f" | {str(self.status):<20}"
            + f" | {tasks_count:>3} tasks"
        )
        return description

    def get_release_notes(self, revision_from, revision_to) -> str:
        """Returns release notes for component"""
        if self.repo is None:
            return ""

        if self.repo.git_cloud == GitCloudService.GITHUB:
            return get_release_notes_github(
                revision_from, revision_to, self.repo.url, self.__tasks
            )
        if self.repo.git_cloud == GitCloudService.BITBUCKET:
            return get_release_notes_bitbucket(self.__tasks)

        return ""


class NovaEmptyComponent(NovaComponent):
    """
    Represents empty Nova component.
    It is used to group tasks only. According to convention it is
    named 'N/A' or 'n/a' in Jira.
    """

    default_component_name = "n/a"
    component_names = [default_component_name, "multiple components"]

    def __init__(self):
        super().__init__(NovaEmptyComponent.default_component_name, None)

    @classmethod
    def parse(cls, component_name: str):
        """Parses component name"""
        normalized = component_name.strip().lower()
        if normalized in NovaEmptyComponent.component_names:
            return NovaEmptyComponent()
        return None
