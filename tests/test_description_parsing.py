"""
Jira component decscription parsing tests
"""

import pytest

from release_manager import parse_jira_cmp_descr
from core.cvs import GitCloudService


@pytest.mark.parametrize("descr", [None, "", " "])
def test_when_empty_returns_none(descr):
    cloud, url = parse_jira_cmp_descr(descr)
    assert cloud is None
    assert url is None


@pytest.mark.parametrize("descr", ["string", "just sentence", "cloud:", ":url"])
def test_when_invalid_format_returns_none(descr):
    cloud, url = parse_jira_cmp_descr(descr)
    assert cloud is None
    assert url is None


@pytest.mark.parametrize("descr", ["http://example.com"])
def test_when_unknown_cloud_returns_none(descr):
    cloud, url = parse_jira_cmp_descr(descr)
    assert cloud is None
    assert url is None


@pytest.mark.parametrize("descr,expected",
                         [("http://github.com/company/repo.git", GitCloudService.GITHUB),
                          ("http://github.com/company/repo", GitCloudService.GITHUB),
                             ("http://bitbucket.org/company/project.git",
                              GitCloudService.BITBUCKET),
                             ("http://bitbucket.org/company/project",
                              GitCloudService.BITBUCKET),
                             ("https://github.com/company/repo.git",
                              GitCloudService.GITHUB),
                             ("https://bitbucket.org/company/project.git",
                              GitCloudService.BITBUCKET),
                             ("bitbucket.org/company/project.git",
                              GitCloudService.BITBUCKET),
                             ("bitbucket.org/company/project", GitCloudService.BITBUCKET)])
def test_happy_path(descr, expected):
    cloud, url = parse_jira_cmp_descr(descr)
    assert cloud == expected
    assert url == descr
