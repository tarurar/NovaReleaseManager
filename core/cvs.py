"""The module contains classes to keep info about CVS repositories."""
from enum import Enum, auto


class GitCloudService(Enum):
    """
    Git cloud service type
    """

    UNDEFINED = "undefined"
    GITHUB = "github"
    BITBUCKET = "bitbucket"


class CodeRepository:
    """
    Represents Nova component code repository
    """

    def __init__(self, git_cloud: GitCloudService, url: str):
        self.__git_cloud = git_cloud
        self.__url = url

    @property
    def url(self):
        """Repository url"""
        return self.__url

    @property
    def git_cloud(self):
        """Git cloud service"""
        return self.__git_cloud
