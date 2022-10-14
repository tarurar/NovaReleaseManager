"""
The release manager is responsible for managing the release process.
"""
from locale import normalize
import logging
from urllib.parse import urlparse
from jira import JIRA, JIRAError
from github import Github
from git import Repo, Tag

from core.cvs import GitCloudService, CodeRepository
from core.nova_component import NovaComponent
from core.nova_release import NovaRelease
from core.nova_status import Status
from core.nova_task import NovaTask


def parse_jira_component_description(description: str) -> tuple[GitCloudService, str]:
    """Parse Jira component description and return cloud service and repository URL"""
    if description is None:
        return None, None

    normalized_description = description.lower()
    url = normalized_description.split(':')[1]
    if normalized_description.startswith('github'):
        return GitCloudService.GITHUB, url
    if normalized_description.startswith('bitbucket'):
        return GitCloudService.BITBUCKET, url

    url_parse_result = urlparse(url)
    if url_parse_result.hostname is None:
        return None, None
    if 'github' in url_parse_result.hostname:
        return GitCloudService.GITHUB, url
    if 'bitbucket' in url_parse_result.hostname:
        return GitCloudService.BITBUCKET, url
    return None, None


class ReleaseManager:
    """The release manager is responsible for managing the release process."""

    # todo: add dependant client packages update validation. Common issue: package updated but not mentioned in release notes
    # todo: add jira components validation (all have type and url)

    def __init__(self, jira_client: JIRA, github_client: Github) -> None:
        self.__j = jira_client
        self.__g = github_client

    def __get_jira_issues(self, project: str, fix_version: str) -> list:
        result = []
        i = 0
        chunk_size = 50
        jql = f'project={project} and fixVersion="{fix_version}" order by Component asc'
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

        component_tasks = {}
        for issue in self.__get_jira_issues(project, str(release)):
            # todo: add issue validation for multiple components, only one component is allowed, it is required at the same time
            if len(issue.fields.components) == 0:
                logging.warning(
                    'Issue %s has no components, skipping', issue.key)
                continue
            issue_component = issue.fields.components[0].name
            if issue_component not in component_tasks:
                component_tasks[issue_component] = []
            component_tasks[issue_component].append(issue)

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
            (git_cloud, repo_url) = parse_jira_component_description(
                filtered_jira_components[0].description)
            if git_cloud is None or repo_url is None:
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

        # if component.get_status() == Status.Done:
        #     raise Exception(
        #         f'Component [{component.name}] is already released')

        # if component.get_status() != Status.ReadyForRelease:
        #     raise Exception(
        #         f'Component [{component.name}] is not ready for release')

        if component.repo.git_cloud != GitCloudService.GITHUB:
            raise Exception('Only GitHub repositories are currently supported')

        repo = self.__g.get_repo(component.repo.url)
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
