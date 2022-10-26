"""
The release manager is responsible for managing the release process.
"""

import logging
from typing import Optional
from urllib.parse import urlparse
import validators
from jira import JIRA, JIRAError
from github import Github
from git import Tag

from core.cvs import GitCloudService, CodeRepository
from core.nova_component import NovaComponent
from core.nova_release import NovaRelease
from core.nova_status import Status
from core.nova_task import NovaTask


def parse_jira_cp_descr(description: str) -> tuple[Optional[GitCloudService], Optional[str]]:
    """
    Parse Jira component description and return cloud service and repository URL.
    It is epected that JIRA component description will be in the following format:
        Bitbucket repository: http(s)://bitbucket.org/<repository>
        GitHub repository: http(s)://github.com/<company>/<repository> or
            just <company>/<repository>
    """
    if description is None:
        return None, None

    normalized_description = description.strip().lower()

    if not normalized_description.startswith('http'):
        normalized_description = 'http://' + normalized_description

    if validators.url(normalized_description):
        url_parse_result = urlparse(normalized_description)
        if 'github' in url_parse_result.hostname:
            return GitCloudService.GITHUB, description
        if 'bitbucket' in url_parse_result.hostname:
            return GitCloudService.BITBUCKET, description
    return None, None


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


def validate_jira_issues(issues: list) -> str:
    """
    Validate Jira issues.
    Returns error message for the first invalid issue found.
    """
    if len(issues) == 0:
        return 'No issues found'

    for issue in issues:
        if len(issue.fields.components) == 0:
            return f'Issue [{issue.key}] has no component'
        if len(issue.fields.components) > 1:
            return f'Issue [{issue.key}] has more than one component'
        if issue.fields.status.name != 'Selected For Release':
            return f'Issue [{issue.key}] expected to have status [Selected For Release]'
    return ''


def validate_jira_components(components: list) -> str:
    """
    Validate Jira components.
    Returns error message for the first invalid component found.
    """
    if len(components) == 0:
        return 'No components found'

    for component in components:
        if not hasattr(component, 'name'):
            return 'Component has no name'
        if not hasattr(component, 'description'):
            return f'Component [{component.name}] has no description'
        if component.name is None:
            return 'Component name is empty'
        if component.description is None or component.description.strip() == '':
            return f'Component [{component.name}] has empty description'

        cloud_service, repo_url = parse_jira_cp_descr(component.description)
        if cloud_service is None or repo_url is None:
            return f'Component [{component.name}] has invalid description, ' \
                f'expected to be in the following format: ' \
                f'Bitbucket repository: http(s)://bitbucket.org/<repository> or ' \
                f'GitHub repository: http(s)://github.com/<company>/<repository> or ' \
                f'just <company>/<repository>'
    return ''


class ReleaseManager:
    """The release manager is responsible for managing the release process."""
    # todo: add dependant client packages update validation.
    # Common issue: package updated but not mentioned in release notes
    # todo: add jira components validation (all have type and url)

    def __init__(self, jira_client: JIRA, github_client: Github) -> None:
        self.__j = jira_client
        self.__g = github_client

    def __get_jira_issues(self, project: str, fix_version: str, component='') -> list:
        result = []
        i = 0
        chunk_size = 50

        jql = build_jql(project, fix_version, component)
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

    def get_release(self, project: str, version: str, delivery: str) -> NovaRelease:
        """Get release by project, version and delivery"""
        release = NovaRelease(project, version, delivery)

        jira_issues = self.__get_jira_issues(project, str(release))
        jira_issues_error = validate_jira_issues(jira_issues)
        if jira_issues_error:
            raise Exception(jira_issues_error)

        component_tasks = {}
        for i in jira_issues:
            name = i.fields.components[0].name
            component_tasks[name].append(i)

        jira_components = self.__j.project_components(project)

        for (k, v) in component_tasks.items():
            matches = filter(lambda x: x.name == k, jira_components)
            filtered_jira_components = list(matches)
            if len(filtered_jira_components) == 0:
                raise Exception(f'Component [{k}] not found in Jira')
            if len(filtered_jira_components) > 1:
                raise Exception(f'Component [{k}] is not unique in Jira')
            if not hasattr(filtered_jira_components[0], 'description'):
                logging.warning(
                    'Component [%s] has no description property. Skipping', k)
                continue
            if filtered_jira_components[0].description is None:
                logging.warning(
                    'Component [%s] has no description. Skipping', k)
            (git_cloud, repo_url) = parse_jira_cp_descr(
                filtered_jira_components[0].description)
            if git_cloud is None or repo_url is None:
                if k.strip().lower() != 'n/a':
                    logging.warning(
                        'Component [%s] has invalid description: [%s]. Expected to be repository url. Skipping', k, filtered_jira_components[0].description)
                continue
            component = NovaComponent(k, CodeRepository(git_cloud, repo_url))
            jira_tasks = component_tasks[k]
            for jira_task in jira_tasks:
                nova_task = NovaTask(jira_task.key, NovaTask.map_jira_issue_status(
                    jira_task.fields.status.name))
                component.add_task(nova_task)
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
