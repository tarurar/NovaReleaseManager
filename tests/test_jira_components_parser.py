"""
Jira issues parser tests
"""
import pytest
from jira_utils import parse_jira_component
from core.nova_component import NovaComponent, NovaEmptyComponent


class MockedComponent:
    """Mock Jira component"""

    def __init__(self, name, description):
        self.name = name
        self.description = description


class MockedNamelessComponent:
    """Mock nameless Jira component"""

    def __init__(self, description):
        self.description = description


class MockedDescriptionlessComponent:
    """Mock descriptionless Jira component"""

    def __init__(self, name):
        self.name = name


def test_when_empty_component_provided():
    with pytest.raises(ValueError):
        parse_jira_component(None)


def test_when_component_has_no_description():
    component = MockedComponent("component name", None)
    with pytest.raises(ValueError):
        parse_jira_component(component)


def test_when_component_has_no_description_attr():
    component = MockedDescriptionlessComponent("component name")
    with pytest.raises(ValueError) as excinfo:
        parse_jira_component(component)

    assert "no description" in str(excinfo.value)


def test_when_component_has_no_name():
    component = MockedComponent(None, "component description")
    with pytest.raises(ValueError):
        parse_jira_component(component)


def test_when_component_has_no_name_attr():
    component = MockedNamelessComponent("component description")
    with pytest.raises(ValueError) as excinfo:
        parse_jira_component(component)

    assert "no name" in str(excinfo.value)


def test_when_component_has_invalid_description():
    component = MockedComponent("component name", "invalid description")
    with pytest.raises(ValueError):
        parse_jira_component(component)


def test_when_component_is_valid():
    component = MockedComponent(
        "component name", "http://github.com/company/project"
    )
    result = parse_jira_component(component)
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
    component = MockedComponent(component_name, "")
    result = parse_jira_component(component)
    assert isinstance(result, NovaEmptyComponent)
    assert result.name == NovaEmptyComponent.default_component_name


def teardown_module():
    """Teardown module"""
    NovaComponent.longest_component_name = 0
