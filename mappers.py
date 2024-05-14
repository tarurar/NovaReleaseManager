"""
Data mapping and filtering functions
"""

from git import TagReference
from core.nova_component import NovaComponent
from core.nova_component_type import NovaComponentType
from git_utils import get_git_tag_url
from notes_generator import NotesGenerator


def map_to_tag_info(package: NovaComponent, tag: TagReference):
    """
    Map package and tag to tag info
    """
    if package.repo is None:
        raise ValueError("Package repository is not specified")

    return {
        "package": package.name,
        "tag": tag.name,
        "date": tag.commit.committed_datetime.strftime("%Y-%m-%d"),
        "url": get_git_tag_url(
            package.repo.git_cloud, package.repo.sanitized_url, tag.name
        ),
    }


def is_service_tag(service: NovaComponent, tag: TagReference) -> bool:
    """
    Detects if tag is service tag.
    """

    tag_name = tag.name.lower()

    if service.ctype != NovaComponentType.SERVICE:
        return False

    if tag_name.startswith("v") or tag_name.startswith("nova"):
        return True

    return False


def is_package_tag(package: NovaComponent, tag: TagReference) -> bool:
    """
    Detects if tag is package tag.
    Taking into account that git repositories can host not only nuget packages
    but services as well, there might be tags related to packages and services
    releases. This function detects if tag is package tag or not.
    Here are the rules:
        - if tag name starts with "client", "contract" or "domain" then it is
        package tag (client library)
        - if tag name starts with "v" then it is package tag (infrastucture
        library)
    """

    tag_name = tag.name.lower()
    # there are packages which are libraries but do not follow the rule
    # and have client-... or contract-... prefix due to historical reasons
    if (
        tag_name.startswith("client")
        or tag_name.startswith("contract")
        or tag_name.startswith("domain")
    ):
        return True

    # however, if package is infrastructure library then it should follow the
    # rule and have "v" prefix. Still while migrating to new rules we still
    # might have tags which do not follow the rule. This is temporary solution
    if package.ctype == NovaComponentType.PACKAGE_LIBRARY:
        return True

    return False


def only_succeeded_notes(
    notes: dict[str, NotesGenerator.Result]
) -> dict[str, str]:
    """
    Filters out notes which were not generated successfully
    """
    return {k: v.path for k, v in notes.items() if v.path and not v.error}
