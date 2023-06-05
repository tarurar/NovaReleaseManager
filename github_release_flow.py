"""
The module describes the component release flow for the
GitHub hosted repositories.
"""

from typing import Optional
from github import Github
from github.Repository import Repository
from github.Tag import Tag
from github.GitRelease import GitRelease
from core.nova_component import NovaComponent
from core.nova_release import NovaRelease
import github_utils as gu
from ui import console


class GitHubReleaseFlow:
    """
    The class describes the component release flow for the
    GitHub hosted repositories. Takes care of the GitHub API interaction.
    """

    def __init__(self, github: Github, branch: str = 'master'):
        self.__g = github
        self.__branch = branch

    def __get_repository(self, url: str) -> Repository:
        """
        Returns GitHub repository object.

        :param url: repository url
        :return: GitHub repository object
        """
        compatible_url = gu.get_github_compatible_repo_address(url)

        repo = self.__g.get_repo(compatible_url)
        if repo is None:
            raise IOError(f'Could not find repository [{url}]')

        return repo

    def tag_to_text(self, tag: Tag) -> str:
        """
        Creates a text representation of the tag.

        :param tag: Tag object
        :return: text representation of the tag
        """
        return (
            f'{tag.name}'
            f' @ {tag.commit.commit.last_modified}'
            f'by {tag.commit.commit.author.name}')

    def get_repository_top_tags(
            self, url: str, tags_count: int = 5) -> list[Tag]:
        """
        Returns the list of the top tags for the repository
        sorted by the last commit date and formatted as text.

        :param url: repository url
        :param tags_count: number of tags to return
        :return: list of the top Tag objects
        """
        repo = self.__get_repository(url)
        tags = list(repo.get_tags())[:tags_count]
        return tags

    def create_tag(
            self, repo_url: str, message: str, tag_name: str) -> Tag:
        """
        Creates a Tag object in the repository which points to the
        latest commit.

        :param repo_url: repository url
        :param message: tag message
        :param tag_name: tag name
        :return: Tag object
        """
        repo = self.__get_repository(repo_url)
        latest_commit = repo.get_branch(self.__branch).commit
        repo.create_git_tag(tag_name, message, latest_commit.sha, 'commit')

        tags_dict = {tag.name: tag for tag in repo.get_tags()}
        tag = tags_dict.get(tag_name)

        if tag is None:
            raise IOError(f'Could not create tag [{tag_name}]')

        return tag

    def select_or_create_tag(self, url: str, tag_message: str) -> Optional[Tag]:
        """
        Returns the Tag object selected by the user or creates
        a new Tag object.
        If user neither selects nor creates a tag, returns None.

        :param url: repository url
        :param tag_message: tag message
        :return: Tag object or None
        """
        top_tags = self.get_repository_top_tags(url)
        top_tag_names = list(map(self.tag_to_text, top_tags))

        print('Please, choose a tag:')
        selected_index = console.choose_from_or_skip(top_tag_names)
        if selected_index:
            return top_tags[selected_index]

        tag_name = console.input_tag_name()
        if tag_name is None:
            return None
        return self.create_tag(url, tag_message, tag_name)

    def select_or_autodetect_tag(
            self, url: str, exclude: list[str]) -> Optional[Tag]:
        """
        Returns the Tag object selected by the user or autodetected
        from the repository. Autodetection takes the latest tag.
        If user neither selects nor there is no tag in the repository,
        returns None.

        :param url: repository url
        :param exclude: list of the tag names to exclude from the auto detection
        :return: Tag object or None
        """
        top_tags = self.get_repository_top_tags(url)
        top_tag_names = list(map(self.tag_to_text, top_tags))

        print('Please, choose a tag:')
        selected_index = console.choose_from_or_skip(top_tag_names)
        if selected_index:
            return top_tags[selected_index]

        for tag in top_tags:
            if tag.name not in exclude:
                return tag

        return None

    def create_git_release(
            self,
            release: NovaRelease,
            component: NovaComponent) -> Optional[GitRelease]:
        """
        Creates a GitRelease object in the repository.

        :param release: NovaRelease object
        :param component: NovaComponent object
        :return: GitRelease object or None
        """
        # get a tag for the git release
        tag = self.select_or_create_tag(component.repo.url, release.title)
        if tag is None:
            return None

        # get a tag for previous git release
        previous_tag = self.select_or_autodetect_tag(
            component.repo.url, list(tag.name))
        if previous_tag is None:
            return None

        # create git release
        repo = self.__get_repository(component.repo.url)
        git_release_notes = component.get_release_notes(
            previous_tag.name, tag.name)
        git_release = repo.create_git_release(
            tag.name, release.title, git_release_notes)
        if git_release is None:
            raise IOError(f'Could not create release for tag {tag.name}')

        return git_release
