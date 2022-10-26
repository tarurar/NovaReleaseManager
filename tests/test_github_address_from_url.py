"""
Jira component decscription parsing tests
"""

import pytest

from release_manager import get_github_repository_address


@pytest.mark.parametrize("url, expected",
                         [("host/company/repo", "company/repo"),
                          ("host/company/repo.git", "company/repo.git")])
def test_when_url_does_not_start_with_schema(url, expected):
    address = get_github_repository_address(url)
    assert address == expected


@pytest.mark.parametrize("url, expected",
                         [("http://host/company/repo", "company/repo"),
                          ("https://host/company/repo", "company/repo")])
def test_when_url_starts_with_schema(url, expected):
    address = get_github_repository_address(url)
    assert address == expected
