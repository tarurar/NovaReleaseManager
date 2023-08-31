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
    def sanitized_url(self):
        """Repository url without credentials"""
        return CodeRepository.sanitize_git_url(self.__url)

    @property
    def git_cloud(self):
        """Git cloud service"""
        return self.__git_cloud

    @staticmethod
    def sanitize_git_url(url: str) -> str:
        """
        Removes username and password from Git URL.

        :param url: Git URL.
        :return: sanitized Git URL.
        """
        if not url:
            return ""

        # The presence of "@" in the URL indicates that the URL contains
        # username and password.
        if "@" not in url:
            return url

        # The URL contains username and password. Remove them.
        url_parts = url.split("@")
        if len(url_parts) != 2 or not url_parts[1]:
            raise ValueError(f"Invalid URL format: {url}")

        schema = ""
        if url.startswith("http"):
            schema = url_parts[0].split("://")[0]

        url = f"{schema}://{url_parts[1]}" if schema else url_parts[1]
        return url
