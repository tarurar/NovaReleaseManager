"""
Data mapping functions
"""

from git import TagReference
from core.nova_component import NovaComponent
from git_utils import get_git_tag_url


def map_to_tag_info(package: NovaComponent, tag: TagReference):
    """
    Map package and tag to tag info
    """

    return {
        "package": package.name,
        "tag": tag.name,
        "date": tag.commit.committed_datetime.strftime("%Y-%m-%d"),
        "url": get_git_tag_url(
            package.repo.git_cloud, package.repo.url, tag.name
        ),
    }
