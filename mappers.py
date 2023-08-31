"""
Data mapping and filtering functions
"""

from git import TagReference
from core.nova_component import NovaComponent
from core.nova_component_type import NovaComponentType
from git_utils import get_git_tag_url, sanitize_git_url


def map_to_tag_info(package: NovaComponent, tag: TagReference):
    """
    Map package and tag to tag info
    """
    if package.repo is None:
        raise ValueError("Package repository is not specified")

    sanitized_url = sanitize_git_url(package.repo.url)

    return {
        "package": package.name,
        "tag": tag.name,
        "date": tag.commit.committed_datetime.strftime("%Y-%m-%d"),
        "url": get_git_tag_url(package.repo.git_cloud, sanitized_url, tag.name),
    }


def is_package_tag(package: NovaComponent, tag: TagReference) -> bool:
    """
    Detects if tag is package tag.
    Taking into account that git repositories can host not only nuget packages
    but services as well, there might be tags related to packages and services
    releases. This function detects if tag is package tag or not.
    Here is the rule:
        - if tag name starts with "client" or "contract" then it is package tag
        - if tag name starts with "v" then it is package tag
    """

    tag_name = tag.name.lower()
    if tag_name.startswith("client") or tag_name.startswith("contract"):
        return package.ctype == NovaComponentType.PACKAGE

    if tag_name.startswith("v"):
        return package.ctype == NovaComponentType.PACKAGE_LIBRARY

    return False
