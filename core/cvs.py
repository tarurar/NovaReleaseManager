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
        self.git_cloud = git_cloud
        self.url = url
