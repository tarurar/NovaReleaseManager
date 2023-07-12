"""
Git integration layer module.
"""


import tempfile
from typing import Optional
from git.repo import Repo


class GitIntegration:
    """
    Git integration service.
    Connects to Git using ...
    """

    def __init__(self, branch: str = 'master') -> None:
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
            raise ValueError('Repository url is not specified')

        if sources_dir is None:
            sources_dir = tempfile.mkdtemp(prefix='nova')

        Repo.clone_from(url, sources_dir, branch=self.__branch)

        return sources_dir

    def commit(self, repo_dir: str, commit_message: str) -> None:
        """
        Commit changes in the repository

        :param repo_dir: path to the repository
        :param commit_message: commit message
        """
        if not repo_dir:
            raise ValueError('Repository directory is not specified')

        if not commit_message:
            raise ValueError('Commit message is not specified')

        repo = Repo(repo_dir)
        repo.git.add('--all')
        repo.git.commit('-m', commit_message)
        repo.git.push()

    def tag(self, repo_dir: str, tag_name: str, tag_message: str) -> None:
        """
        Create a tag in the repository
        :param repo_dir: path to the repository
        :param tag_name: tag name
        :param tag_message: tag message
        """
        if not repo_dir:
            raise ValueError('Repository directory is not specified')

        if not tag_name:
            raise ValueError('Tag name is not specified')

        if not tag_message:
            raise ValueError('Tag message is not specified')

        repo = Repo(repo_dir)
        repo.create_tag(tag_name, message=tag_message)
        repo.git.push('origin', tag_name)
