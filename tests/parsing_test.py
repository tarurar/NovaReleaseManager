import pytest

from release_manager import parse_jira_component_description
from core.cvs import GitCloudService


@pytest.mark.parametrize("input", [None, "", " "])
def test_parse_jira_component_description_when_empty_returns_none(input):
    cloud, str = parse_jira_component_description(input)
    assert cloud is None
    assert str is None

@pytest.mark.parametrize("input", ["string", "just sentence", "cloud:", ":url"])
def test_parse_jira_component_description_when_invalid_format_returns_none(input):
    cloud, str = parse_jira_component_description(input)
    assert cloud is None
    assert str is None

@pytest.mark.parametrize("input", ["cloud:url", ":url", "cloud:http://example.com"])
def test_parse_jira_component_description_when_unknown_cloud_returns_none(input):
    cloud, str = parse_jira_component_description(input)
    assert cloud is None
    assert str is None

@pytest.mark.parametrize("input", ["cloud:url", "cloud:", "github:url", "github:"])
def test_parse_jira_component_description_when_not_url_returns_none(input):
    cloud, str = parse_jira_component_description(input)
    assert cloud is None
    assert str is None

@pytest.mark.parametrize("input,expected", 
[("http://github.com/company/repo.git", GitCloudService.GITHUB), 
("http://github.com/company/repo", GitCloudService.GITHUB), 
("http://bitbucket.org/company/project.git", GitCloudService.BITBUCKET), 
("http://bitbucket.org/company/project", GitCloudService.BITBUCKET),
("https://github.com/company/repo.git", GitCloudService.GITHUB), 
("https://bitbucket.org/company/project.git", GitCloudService.BITBUCKET),
("bitbucket.org/company/project.git", GitCloudService.BITBUCKET),
("bitbucket.org/company/project", GitCloudService.BITBUCKET)])
def test_parse_jira_component_description_when_only_url_returns_result(input, expected):
    cloud, _ = parse_jira_component_description(input)
    assert cloud == expected
