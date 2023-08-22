"""
Git utility helper function module.
"""

from core.cvs import GitCloudService


def get_git_tag_url(
    git_cloud: GitCloudService, base_url: str, tag_name: str
) -> str:
    """
    Returns Git tag URL.

    :param git_cloud: Git cloud service.
    :param base_url: Git repository base URL.
    :param tag_name: tag name.
    :return: Git tag URL.
    """

    if not base_url:
        raise ValueError("Base URL is not specified")

    if not tag_name:
        raise ValueError("Tag name is not specified")

    if base_url.endswith("/"):
        base_url = base_url[:-1]
    if base_url.endswith(".git"):
        base_url = base_url[:-4]

    if git_cloud == GitCloudService.GITHUB:
        return f"{base_url}/releases/tag/{tag_name}"

    if git_cloud == GitCloudService.BITBUCKET:
        return f"{base_url}/src/{tag_name}"

    raise ValueError(f"Unsupported Git cloud service: {git_cloud}")
