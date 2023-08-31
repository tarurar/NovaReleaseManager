"""
The module describes the component release flow for the
GitHub hosted repositories.
"""

import time
from typing import Optional
from github import Github
from github.Repository import Repository
from github.Tag import Tag
import github_utils as gu
from ui import console


class GitHubIntegration:
    """
    The class describes the component release flow for the
    GitHub hosted repositories. Takes care of the GitHub API integration.
    """

    def __init__(self, github: Github, branch: str = "master"):
        self.__g = github
        self.__branch = branch

    def get_repository(self, url: str) -> Repository:
        """
        Returns GitHub repository object.

        :param url: repository url
        :return: GitHub repository object
        """
        compatible_url = gu.get_github_compatible_repo_address(url)

        repo = self.__g.get_repo(compatible_url)
        if repo is None:
            raise IOError(f"Could not find repository [{url}]")

        return repo

    def get_repository_top_tags(
        self, url: str, tags_count: int = 5
    ) -> list[Tag]:
        """
        Returns the list of the top tags for the repository
        sorted by the last commit date and formatted as text.

        :param url: repository url
        :param tags_count: number of tags to return
        :return: list of the top Tag objects
        """
        repo = self.get_repository(url)
        tags = list(repo.get_tags())[:tags_count]
        return tags

    def create_tag(self, repo_url: str, message: str, tag_name: str) -> Tag:
        """
        Creates a Tag object in the repository which points to the
        latest commit.
        In case of failure, raises IOError but retries 3 times before.

        :param repo_url: repository url
        :param message: tag message
        :param tag_name: tag name
        :return: Tag object
        """
        repo = self.get_repository(repo_url)
        latest_commit = repo.get_branch(self.__branch).commit
        new_git_tag = repo.create_git_tag(
            tag_name, message, latest_commit.sha, "commit"
        )
        repo.create_git_ref(f"refs/tags/{new_git_tag.tag}", new_git_tag.sha)

        # retry here since it takes some time for the tag to appear
        tag = None
        for _ in range(3):
            tags_dict = {tag.name: tag for tag in repo.get_tags()}
            tag = tags_dict.get(tag_name)
            if tag:
                break
            time.sleep(3)

        if tag is None:
            raise IOError(f"Could not create tag [{tag_name}]")

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
        top_tag_names = list(map(gu.tag_to_text, top_tags))

        print("Please, choose a tag:")
        selected_index = console.choose_from_or_skip(top_tag_names)
        if selected_index is not None:
            return top_tags[selected_index]

        tag_name = console.input_tag_name()
        if tag_name is None:
            return None
        return self.create_tag(url, tag_message, tag_name)

    def select_or_autodetect_tag(
        self, url: str, exclude: list[str]
    ) -> Optional[Tag]:
        """
        Returns the Tag object selected by the user or autodetected
        from the repository. Autodetection takes the latest tag.
        If user neither selects one nor there is a tag in the repository,
        returns None.

        :param url: repository url
        :param exclude: list of the tag names to exclude from the auto detection
        :return: Tag object or None
        """
        top_tags = self.get_repository_top_tags(url)
        top_tag_names = list(map(gu.tag_to_text, top_tags))

        print("Please, choose a tag:")
        selected_index = console.choose_from_or_skip(top_tag_names)
        if selected_index:
            return top_tags[selected_index]

        for tag in top_tags:
            if tag.name not in exclude:
                return tag

        return None
