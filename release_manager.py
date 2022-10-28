"""
The release manager is responsible for managing the release process.
"""

import logging

from jira import JIRA, JIRAError
from github import Github
from git import Tag

from core.cvs import GitCloudService, CodeRepository
from core.nova_component import NovaComponent, NovaEmptyComponent
from core.nova_release import NovaRelease
from core.nova_status import Status
from core.nova_task import NovaTask
from jira_utils import parse_jira_cmp_descr


def get_github_compatible_repo_address(full_url: str) -> str:
    """
    Returns GitHub client compatible repository address.
    The address returned can be used with official GitHub API client to access the repository.
    It will be provided in the following format:
        <company>/<repository>
    """
    normalized = full_url.strip().lower()
    if normalized.startswith('http'):
        normalized = normalized.replace('http://', '').replace('https://', '')

    chunks = normalized.split('/')
    return '/'.join(chunks[1:])


def build_jql(project: str, fix_version='', component='') -> str:
    """
    Build JQL query string.
    """
    jql = f'project={project}'
    if fix_version:
        jql += f' AND fixVersion="{fix_version}"'
    if component:
        jql += f' AND component="{component}"'
    return jql


def parse_jira_component(cmp: object) -> NovaComponent:
    """
    Parse Jira component.
    """
    if cmp is None:
        raise ValueError('Component is None')
    if not hasattr(cmp, 'name'):
        raise ValueError('Component has no name')
    if cmp.name is None:
        raise ValueError('Component name is empty')
    if cmp.name.strip().lower() == NovaEmptyComponent.default_component_name:
        return NovaEmptyComponent()
    if not hasattr(cmp, 'description'):
        raise ValueError(f'Component [{cmp.name}] has no description')
    if cmp.description is None or cmp.description.strip() == '':
        raise ValueError(f'Component [{cmp.name}] has empty description')

    cloud_service, repo_url = parse_jira_cmp_descr(cmp.description)
    if cloud_service is None or repo_url is None:
        raise ValueError(f'Component [{cmp.name}] has invalid description, '
                         f'expected to be in the following format: '
                         f'Bitbucket: http(s)://bitbucket.org/<repo> or '
                         f'GitHub: http(s)://github.com/<company>/<repo> or '
                         f'just <company>/<repo>')

    return NovaComponent(
        cmp.name,
        CodeRepository(cloud_service, repo_url))


def parse_jira_issue(jira_issue: object) -> NovaTask:
    """
    Parse Jira issue.
    """
    if jira_issue is None:
        raise ValueError('Issue is None')
    if not hasattr(jira_issue, 'key'):
        raise ValueError('Issue has no key')
    if not jira_issue.key:
        raise ValueError('Issue key is empty')
    if len(jira_issue.fields.components) == 0:
        raise ValueError(f'Issue [{jira_issue.key}] has no component')
    if len(jira_issue.fields.components) > 1:
        raise ValueError(
            f'Issue [{jira_issue.key}] has more than one component')

    status = NovaTask.map_jira_issue_status(jira_issue.fields.status.name)
    if status == Status.UNDEFINED:
        raise ValueError(
            f'Issue [{jira_issue.key}] has invalid status [{jira_issue.fields.status.name}]')

    return NovaTask(jira_issue.key, status)


def filter_jira_issue(jira_issue, cmp_name) -> bool:
    """
    Filter Jira issue by component name.
    """
    jira_name = jira_issue.fields.components[0].name.strip().lower()
    nova_name = cmp_name.strip().lower()

    return jira_name == nova_name


class ReleaseManager:
    """The release manager is responsible for managing the release process."""
    # todo: add dependant client packages update validation.
    # Common issue: package updated but not mentioned in release notes

    def __init__(self, jira_client: JIRA, github_client: Github) -> None:
        self.__j = jira_client
        self.__g = github_client

    def __get_jira_issues(self, project: str, fix_version: str, cmp='') -> list:
        result = []
        i = 0
        chunk_size = 50

        jql = build_jql(project, fix_version, cmp)
        while True:
            try:
                issues = self.__j.search_issues(
                    jql, maxResults=chunk_size, startAt=i)
            except JIRAError:
                return []
            i += chunk_size
            result += issues.iterable
            if i >= issues.total:
                break
        return result

    def compose(self, project: str, version: str, delivery: str) -> NovaRelease:
        """Get release by project, version and delivery"""
        release = NovaRelease(project, version, delivery)

        components = [parse_jira_component(cmp)
                      for cmp in self.__j.project_components(project)]

        release_jira_issues = self.__get_jira_issues(project, release)

        for component in components:
            component_jira_issues = filter(
                lambda i, c_name=component.name: filter_jira_issue(i, c_name),
                release_jira_issues)
            component_tasks = [parse_jira_issue(issue)
                               for issue in component_jira_issues]
            if len(component_tasks) > 0:
                component.add_tasks(component_tasks)
                release.add_component(component)

        return release

    def release_component(self, release: NovaRelease, component: NovaComponent) -> None:
        """Release component"""
        if component is None:
            raise Exception('Component is not specified')

        if component.get_status() == Status.DONE:
            raise Exception(
                f'Component [{component.name}] is already released')

        if component.get_status() != Status.READY_FOR_RELEASE:
            raise Exception(
                f'Component [{component.name}] is not ready for release')

        if component.repo.git_cloud != GitCloudService.GITHUB:
            raise Exception('Only GitHub repositories are currently supported')

        repo_url = get_github_compatible_repo_address(component.repo.url)
        repo = self.__g.get_repo(repo_url)
        if repo is None:
            raise Exception(f'Cannot get repository {component.repo.url}')

        tags = repo.get_tags()
        tag = ReleaseManager.choose_existing_tag(list(tags[:5]))
        if tag is None:
            tag_name = ReleaseManager.input_tag_name()
            if tag_name is None:
                return
            sha = repo.get_branch('master').commit.sha
            git_tag = repo.create_git_tag(
                tag_name, release.get_title(), sha, 'commit')
        else:
            git_tag = tag

        git_release = repo.create_git_release(
            git_tag.name, release.get_title(), component.get_release_notes())
        if git_release is None:
            raise Exception(f'Could not create release for tag {git_tag.tag}')

        for t in component.tasks:
            self.__j.transition_issue(
                t.name, 'Done', comment=f'{release.get_title()} released')

    @classmethod
    def input_tag_name(cls) -> str:
        """Input tag"""
        tag_name = input('Enter new tag or just press `q` to quit: ')
        if tag_name == 'q':
            return None
        if tag_name is None or tag_name.strip() == '':
            return cls.input_tag_name()
        return tag_name

    @classmethod
    def choose_existing_tag(cls, existing_tags: list[Tag]) -> Tag:
        """Choose tag from existing tags"""
        if len(existing_tags) == 0:
            return None
        d = {}
        for i, value in enumerate(existing_tags):
            d[i] = value

        for (k, v) in d.items():
            print(f'{k+1}: {v.name} @ {v.last_modified}')

        command = input(
            '\nEnter either tag position number from the list or just press enter for new tag: ')
        if command is None or command.strip() == '':
            return None

        if command.isdigit():
            tag_position = int(command) - 1
            if tag_position in d:
                return d[tag_position]
            else:
                logging.warning('Tag number is not in the list')
                return cls.choose_existing_tag(existing_tags)
        else:
            return cls.choose_existing_tag(existing_tags)
