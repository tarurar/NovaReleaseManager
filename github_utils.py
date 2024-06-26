"""
GitHub utility helper function module.
"""

from github.Tag import Tag


def get_github_compatible_repo_address(full_url: str) -> str:
    """
    Returns GitHub client compatible repository address.
    The address returned can be used with official GitHub API client
    to access the repository. It will be provided in the following
    format: <company>/<repository>
    """
    normalized = full_url.strip().lower()
    if normalized.startswith("http"):
        normalized = normalized.replace("http://", "").replace("https://", "")
    if normalized.endswith(".git"):
        normalized = normalized[:-4]

    chunks = normalized.split("/")
    return "/".join(chunks[1:])


def tag_to_text(tag: Tag) -> str:
    """
    Creates a text representation of the tag.

    :param tag: Tag object
    :return: text representation of the tag
    """
    return (
        f"{tag.name}"
        f" @ {tag.commit.commit.last_modified}"
        f"by {tag.commit.commit.author.name}"
    )
