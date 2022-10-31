"""
GitHub utility helper function module.
"""


def get_github_compatible_repo_address(full_url: str) -> str:
    """
    Returns GitHub client compatible repository address.
    The address returned can be used with official GitHub API client
    to access the repository. It will be provided in the following
    format: <company>/<repository>
    """
    normalized = full_url.strip().lower()
    if normalized.startswith('http'):
        normalized = normalized.replace('http://', '').replace('https://', '')

    chunks = normalized.split('/')
    return '/'.join(chunks[1:])
