"""The module contains classes to keep info about CVS repositories."""
from enum import Enum

from config import Config


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

    def __init__(self, git_cloud: GitCloudService, url: str, config=None):
        if config is None:
            config = Config()

        self.__git_cloud = git_cloud
        self.__url = url

        if self.__git_cloud == GitCloudService.BITBUCKET:
            # for bitbucket url should include user name and password
            # to access it since it is private repository
            self.__url = self.__url.replace(
                "https://",
                f"https://{config.data['bitbucket']['username']}:{config.data['bitbucket']['password']}@",
            )

    @property
    def url(self):
        """Repository url"""
        return self.__url

    @property
    def git_cloud(self):
        """Git cloud service"""
        return self.__git_cloud
