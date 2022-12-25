"""
The release manager is responsible for managing the release process.
"""

import logging

from git import Tag
from github import Github
from jira import JIRA, JIRAError
from jira.resources import Version

import github_utils as gu
import jira_utils as ju
from core.cvs import GitCloudService
from core.nova_component import NovaComponent
from core.nova_release import NovaRelease
from core.nova_status import Status


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

        if component.status == Status.DONE:
            raise Exception(
                f'Component [{component.name}] is already released')

        if component.status != Status.READY_FOR_RELEASE:
            raise Exception(
                f'Component [{component.name}] is not ready for release')

        if component.repo.git_cloud != GitCloudService.GITHUB:
            raise Exception('Only GitHub repositories are currently supported')

        repo_url = gu.get_github_compatible_repo_address(component.repo.url)
        repo = self.__g.get_repo(repo_url)
        if repo is None:
            raise Exception(f'Cannot get repository {component.repo.url}')

        # this call return a list of Tag class instances (not GitTag class instances)
        tags = repo.get_tags()
        top5_tags = list(tags)[:5]
        print(f'Please, choose a tag to release component [{component.name}]')
        tag = ReleaseManager.choose_existing_tag(top5_tags)
        if tag is None:
            tag_name = ReleaseManager.input_tag_name()
            if tag_name is None:
                return
            sha = repo.get_branch('master').commit.sha
            git_tag_name = repo.create_git_tag(
                tag_name, release.title, sha, 'commit').tag
        else:
            git_tag_name = tag.name

        print(
            f'Please, choose a tag of previous component [{component.name}] release')
        previous_tag = ReleaseManager.choose_existing_tag(top5_tags)
        if previous_tag is None:
            logging.warning(
                'Previous release tag was not specified, auto-detection will be used')
            auto_detected_previous_tag_list = list(filter(
                lambda t: t.name != git_tag_name, top5_tags))
            if len(auto_detected_previous_tag_list) > 0:
                previous_tag_name = auto_detected_previous_tag_list[0].name
            else:
                previous_tag_name = ''
            if not previous_tag_name:
                logging.warning(
                    'Auto-detection failed, changelog url will be empty')
            else:
                logging.info(
                    'Auto-detected previous release tag: %s', previous_tag_name)
        else:
            previous_tag_name = previous_tag.name

        git_release = repo.create_git_release(
            git_tag_name,
            release.title,
            component.get_release_notes(previous_tag_name, git_tag_name))
        if git_release is None:
            raise Exception(f'Could not create release for tag {git_tag_name}')

        for task in component.tasks:
            try:
                self.__j.transition_issue(
                    task.name,
                    'Done',
                    comment=f'{release.title} released')
            except JIRAError as error:
                logging.warning(
                    'Could not transition issue %s due to error: %s',
                    task.name,
                    error.text)

    def can_release_version(self, project: str, version: str, delivery: str) -> bool:
        """Checks if release can be marked as DONE"""
        release = self.compose(project, version, delivery)
        if release.can_release_version():
            jira_version = self.__j.get_project_version_by_name(
                project=project, version_name=release.title)
            return ReleaseManager.can_release_jira_version(jira_version)
        return False

    def release_version(self, release: NovaRelease):
        """Marks release as DONE"""
        if release is None:
            raise Exception('Release is not specified')
        jira_version = self.__j.get_project_version_by_name(
            project=release.project, version_name=release.title)
        if jira_version is None:
            raise Exception(f'Cannot find JIRA version {release.title}')
        jira_version.update(released=True)

    @classmethod
    def can_release_jira_version(cls, version: Version) -> bool:
        """Checks if Jira version can be released"""
        if version is None:
            return False
        if version.archived:
            return False
        if version.released:
            return False
        return True

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
        """Choose a tag from existing tags"""
        if not existing_tags:
            return None

        tags_view = {}
        for index, tag in enumerate(existing_tags):
            view_index = index + 1
            tags_view[view_index] = tag
            print(
                f'{view_index}: {tag.name} @ {tag.commit.commit.last_modified} by {tag.commit.commit.author.name}')

        selection = input(
            "\nEnter either tag position number from " +
            "the list or just press enter for new tag: ")
        if selection is None or selection.strip() == '':
            return None

        if selection.isdigit():
            tag_position = int(selection)
            if tag_position in tags_view:
                return tags_view[tag_position]
            else:
                logging.warning('Tag number is not in the list')
                return cls.choose_existing_tag(existing_tags)
        else:
            return cls.choose_existing_tag(existing_tags)
