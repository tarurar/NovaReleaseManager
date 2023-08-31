"""
Git utility helper function tests
"""

import pytest

from core.cvs import GitCloudService
from git_utils import get_git_tag_url, sanitize_git_url


def test_get_git_tag_url_empty_base_url():
    with pytest.raises(ValueError) as excinfo:
        get_git_tag_url(GitCloudService.GITHUB, "", "1.0.0")

    assert "Base URL is not specified" in str(excinfo.value)


def test_get_git_tag_url_empty_tag_name():
    with pytest.raises(ValueError) as excinfo:
        get_git_tag_url(GitCloudService.GITHUB, "http://example.com", "")

    assert "Tag name is not specified" in str(excinfo.value)


@pytest.mark.parametrize(
    "git_cloud,base_url,expected",
    [
        (
            GitCloudService.GITHUB,
            "http://github.com/org/repo",
            "http://github.com/org/repo/releases/tag/1.0.0",
        ),
        (
            GitCloudService.GITHUB,
            "http://github.com/org/repo/",
            "http://github.com/org/repo/releases/tag/1.0.0",
        ),
        (
            GitCloudService.GITHUB,
            "http://github.com/org/repo.git",
            "http://github.com/org/repo/releases/tag/1.0.0",
        ),
        (
            GitCloudService.GITHUB,
            "http://github.com/org/repo.git/",
            "http://github.com/org/repo/releases/tag/1.0.0",
        ),
        (
            GitCloudService.BITBUCKET,
            "http://bitbucket.com/org/repo",
            "http://bitbucket.com/org/repo/src/1.0.0",
        ),
        (
            GitCloudService.BITBUCKET,
            "http://bitbucket.com/org/repo/",
            "http://bitbucket.com/org/repo/src/1.0.0",
        ),
        (
            GitCloudService.BITBUCKET,
            "http://bitbucket.com/org/repo.git",
            "http://bitbucket.com/org/repo/src/1.0.0",
        ),
        (
            GitCloudService.BITBUCKET,
            "http://bitbucket.com/org/repo.git/",
            "http://bitbucket.com/org/repo/src/1.0.0",
        ),
    ],
)
def test_get_git_url(git_cloud: GitCloudService, base_url: str, expected: str):
    assert get_git_tag_url(git_cloud, base_url, "1.0.0") == expected


def test_get_git_url_unsupported_cloud_service():
    with pytest.raises(ValueError):
        get_git_tag_url(
            GitCloudService.UNDEFINED, "http://example.com", "1.0.0"
        )


@pytest.mark.parametrize(
    "url,expected_url",
    [
        ("", ""),
        ("example.com", "example.com"),
        ("user:secret@example.com", "example.com"),
        ("secretr@example.com", "example.com"),
        ("@example.com", "example.com"),
        ("http://example.com", "http://example.com"),
        ("http://user:secret@example.com", "http://example.com"),
        ("http://secret@example.com", "http://example.com"),
        ("http://@example.com", "http://example.com"),
        ("https://example.com", "https://example.com"),
        ("https://user:secret@example.com", "https://example.com"),
        ("https://secret@example.com", "https://example.com"),
        ("https://@example.com", "https://example.com"),
    ],
)
def test_sanitize_git_url(url, expected_url):
    assert sanitize_git_url(url) == expected_url


@pytest.mark.parametrize(
    "invalid_url", ["http://example.com@", "https://example.com@"]
)
def test_sanitize_git_url_raises_exception_when_invalid_format(invalid_url):
    with pytest.raises(ValueError):
        sanitize_git_url(invalid_url)
