"""
Jira issues parser tests
"""
from collections import namedtuple
from unittest.mock import Mock
import pytest
from jira_utils import parse_jira_component
from core.nova_component import NovaComponent, NovaEmptyComponent


@pytest.fixture(name="mock_config")
def fixture_mock_config():
    mock_config = Mock()
    mock_config.data = {
        "github": {"username": "", "accessToken": ""},
        "bitbucket": {"username": "", "password": ""},
    }
    return mock_config


def test_when_empty_component_provided():
    with pytest.raises(ValueError):
        parse_jira_component(None)


def test_when_component_has_no_description():
    component = {"name": "component name", "description": None}
    with pytest.raises(ValueError):
        parse_jira_component(component)


def test_when_component_has_no_description_attr():
    FakeComponent = namedtuple("FakeComponent", ["name"])
    component = FakeComponent("component name")
    with pytest.raises(ValueError) as excinfo:
        parse_jira_component(component)

    assert "no description" in str(excinfo.value)


def test_when_component_has_no_name():
    component = {"name": None, "description": "component description"}
    with pytest.raises(ValueError):
        parse_jira_component(component)


def test_when_component_has_no_name_attr():
    component = {"description": "component description"}
    with pytest.raises(ValueError) as excinfo:
        parse_jira_component(component)

    assert "no name" in str(excinfo.value)


def test_when_component_has_invalid_description():
    component = {"name": "component name", "description": "invalid description"}
    with pytest.raises(ValueError):
        parse_jira_component(component)


def test_when_component_is_valid(mock_config):
    FakeComponent = namedtuple("FakeComponent", ["name", "description"])
    component = FakeComponent(
        "component name", "https://github.com/company/project"
    )
    result = parse_jira_component(component, mock_config)
    assert isinstance(result, NovaComponent)


@pytest.mark.parametrize(
    "component_name",
    [
        "n/a",
        "N/A",
        "N/A ",
        " N/A",
        "N/A  ",
        "n/A",
        "N/a",
        "n/A ",
        " N/a",
        "N/a  ",
    ],
)
def test_when_component_is_named_na(component_name):
    FakeComponent = namedtuple("FakeComponent", ["name", "description"])
    component = FakeComponent(component_name, "")
    result = parse_jira_component(component)
    assert isinstance(result, NovaEmptyComponent)
    assert result.name == NovaEmptyComponent.default_component_name


def teardown_module():
    """Teardown module"""
    NovaComponent.longest_component_name = 0
