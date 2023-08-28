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

        # to access private repositories we need to provide
        # username and password (accessToken for github)
        username = config.data[git_cloud.value]["username"]
        password = (
            config.data[git_cloud.value]["accessToken"]
            if git_cloud == GitCloudService.GITHUB
            else config.data[git_cloud.value]["password"]
        )

        self.__url = self.__url.replace(
            "https://",
            f"https://{username}:{password}@",
        )

    @property
    def url(self):
        """Repository url"""
        return self.__url

    @property
    def git_cloud(self):
        """Git cloud service"""
        return self.__git_cloud
