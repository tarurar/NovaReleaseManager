"""
Git integration layer module.
"""

import tempfile
import time
from datetime import datetime
from operator import attrgetter
from typing import Optional

from git import TagReference
from git.exc import GitCommandError
from git.repo import Repo

from fs_utils import search_files_with_ext, search_changelog_files


class GitIntegration:
    """
    Git integration service.
    Connects to Git using ...
    """

    def __init__(self, branch: str = "master") -> None:
        self.__branch = branch

    def clone(self, url: str, sources_dir: Optional[str] = None) -> str:
        """
        Clone the repository from the given url

        :param url: repository url
        :param sources_dir: directory to clone the repository to. If None
        then a temporary directory will be used.
        :return: path to the cloned repository. The caller is responsible
        for deleting the directory.
        """
        if not url:
            raise ValueError("Repository url is not specified")

        if sources_dir is None:
            sources_dir = tempfile.mkdtemp(prefix="nova")

        Repo.clone_from(url, sources_dir, branch=self.__branch)

        return sources_dir

    def commit_changelogs_and_csproj(
        self, repo_dir: str, commit_message: str
    ) -> None:
        """
        Commit changes in the repository made to only .csproj and
        CHANGELOG.md files at any level of the repository.

        :param repo_dir: path to the repository
        :param commit_message: commit message
        """
        if not repo_dir:
            raise ValueError("Repository directory is not specified")

        if not commit_message:
            raise ValueError("Commit message is not specified")

        csproj_files = search_files_with_ext(repo_dir, ".csproj")
        changelog_files = search_changelog_files(repo_dir)

        repo = Repo(repo_dir)
        repo.git.add(csproj_files)
        repo.git.add(changelog_files)
        repo.git.commit("-m", commit_message)
        repo.git.push()

    def tag(self, repo_dir: str, tag_name: str, tag_message: str) -> None:
        """
        Create a tag in the repository
        :param repo_dir: path to the repository
        :param tag_name: tag name
        :param tag_message: tag message
        """
        if not repo_dir:
            raise ValueError("Repository directory is not specified")

        if not tag_name:
            raise ValueError("Tag name is not specified")

        if not tag_message:
            raise ValueError("Tag message is not specified")

        repo = Repo(repo_dir)
        repo.create_tag(tag_name, message=tag_message)
        repo.git.push("origin", tag_name)

    def checkout(self, repo_dir: str, tag_name: str):
        """
        Checkout the given tag in the repository
        :param repo_dir: path to the repository
        :param tag_name: tag name
        """
        if not repo_dir:
            raise ValueError("Repository directory is not specified")

        if not tag_name:
            raise ValueError("Tag name is not specified")

        repo = Repo(repo_dir)
        repo.git.checkout(tag_name)

    @staticmethod
    def get_latest_tag(repo_dir: str) -> str:
        """
        Get the latest tag in the repository
        :param repo_dir: path to the repository
        :return: latest tag name
        """
        if not repo_dir:
            raise ValueError("Repository directory is not specified")

        repo = Repo(repo_dir)
        tags = sorted(repo.tags, key=attrgetter("commit.committed_datetime"))

        return str(tags[-1])

    @staticmethod
    def list_tags(
        url: str, since: str = "", retry_times=3, retry_interval_sec=5
    ) -> list[TagReference]:
        """
        List tags in the repository since a specified date

        :param url: repository url
        :param since: date in the format YYYY-MM-DD
        :param retry_times: number of times to retry `git clone` operation
            if it fails
        :param retry_interval_sec: interval between retries in seconds
        :return: list of tags
        """
        if not url:
            raise ValueError("Repository url is not specified")

        repo = None
        for _ in range(retry_times):
            try:
                repo = Repo.clone_from(
                    url,
                    tempfile.mkdtemp(prefix="nova"),
                    depth=1,
                    tags=True,
                    no_single_branch=True,
                )
                break
            except GitCommandError:
                time.sleep(retry_interval_sec)

        if not repo:
            raise ValueError(f"Failed to clone the repository ({url})")

        if since:
            since_date = datetime.strptime(since, "%Y-%m-%d").date()
            tags = [
                tag
                for tag in repo.tags
                if tag.commit.committed_datetime.date() >= since_date
            ]
        else:
            tags = list(repo.tags)

        return tags

    def list_tags_with_annotation(
        self, repo_dir: str, annotation: str
    ) -> list[str]:
        """
        Finds tags by annotation applying `contains` operator.
        Returns tag names sorted by date in descending order.

        :param repo_dir: path to the repository.
        :param annotation: annotation to search for.
        :return: list of tag names.
        """
        if not repo_dir:
            raise ValueError("Repository directory is not specified")

        if not annotation:
            raise ValueError("Annotation is not specified")

        repo = Repo(repo_dir)
        filtered_tags = filter(
            lambda tag: (
                annotation in tag.tag.message
                if tag.tag
                else annotation in tag.commit.message
            ),
            repo.tags,
        )

        return list(
            map(
                lambda tag: tag.name,
                sorted(
                    filtered_tags,
                    key=lambda tag: tag.commit.committed_datetime,
                    reverse=True,
                ),
            )
        )
