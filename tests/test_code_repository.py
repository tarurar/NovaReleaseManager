"""
Code repository tests.
"""

import pytest

from core.cvs import CodeRepository


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
    assert CodeRepository.sanitize_git_url(url) == expected_url


@pytest.mark.parametrize(
    "invalid_url", ["http://example.com@", "https://example.com@"]
)
def test_sanitize_git_url_raises_exception_when_invalid_format(invalid_url):
    with pytest.raises(ValueError):
        CodeRepository.sanitize_git_url(invalid_url)
