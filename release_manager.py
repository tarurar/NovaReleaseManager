"""
The release manager is responsible for managing the release process.
"""

import logging

from jira import JIRA, JIRAError
from github import Github
from git import Tag

from core.cvs import GitCloudService
from core.nova_component import NovaComponent
from core.nova_release import NovaRelease
from core.nova_status import Status

import jira_utils as ju
import github_utils as gu


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

        jql = ju.build_jql(project, fix_version, cmp)
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

        components = [ju.parse_jira_component(cmp)
                      for cmp in self.__j.project_components(project)]

        release_jira_issues = self.__get_jira_issues(project, release)

        for component in components:
            component_jira_issues = filter(
                lambda i, cname=component.name: ju.filter_jira_issue(i, cname),
                release_jira_issues)
            component_tasks = [ju.parse_jira_issue(issue)
                               for issue in component_jira_issues]
            if len(component_tasks) > 0:
                component.add_tasks(component_tasks)
                release.add_component(component)

        return release

    def release_component(self, release: NovaRelease, component: NovaComponent):
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

        repo_url = gu.get_github_compatible_repo_address(component.repo.url)
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

        for task in component.tasks:
            self.__j.transition_issue(
                task.name, 'Done', comment=f'{release.get_title()} released')

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
        tags = {}
        for i, value in enumerate(existing_tags):
            tags[i] = value

        for (k, val) in tags.items():
            print(f'{k+1}: {val.name} @ {val.last_modified}')

        command = input("""
            \nEnter either tag position number from 
            the list or just press enter for new tag: """)
        if command is None or command.strip() == '':
            return None

        if command.isdigit():
            tag_position = int(command) - 1
            if tag_position in tags:
                return tags[tag_position]
            else:
                logging.warning('Tag number is not in the list')
                return cls.choose_existing_tag(existing_tags)
        else:
            return cls.choose_existing_tag(existing_tags)
