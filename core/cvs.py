"""The module contains classes to keep info about CVS repositories."""
from enum import Enum


class GitCloudService(Enum):
    """
    Git cloud service type
    """
    GITHUB = 1
    BITBUCKET = 2


class CodeRepository:
    """
    Represents Nova component code repository
    """

    def __init__(self, git_cloud: GitCloudService, url: str):
        self._git_cloud = git_cloud
        self._url = url

    @property
    def url(self):
        """Repository url"""
        return self._url

    @property
    def git_cloud(self):
        """Git cloud service"""
        return self._git_cloud
