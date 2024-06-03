"""
Jira component decscription parsing tests
"""

import pytest

from github_utils import get_github_compatible_repo_address


def test_when_url_does_not_start_with_schema():
    address = get_github_compatible_repo_address("host/company/repo")
    assert address == "company/repo"


@pytest.mark.parametrize(
    "url, expected",
    [
        ("http://host/company/repo", "company/repo"),
        ("https://host/company/repo", "company/repo"),
    ],
)
def test_when_url_starts_with_schema(url, expected):
    address = get_github_compatible_repo_address(url)
    assert address == expected


@pytest.mark.parametrize(
    "url, expected",
    [
        ("host/company/repo.git", "company/repo"),
        ("http://host/company/repo.git", "company/repo"),
        ("https://host/company/repo.git", "company/repo"),
        ("host/company/repo", "company/repo"),
    ],
)
def test_when_url_ends_with_dot_git(url, expected):
    address = get_github_compatible_repo_address(url)
    assert address == expected
