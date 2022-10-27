"""
Jira issues parser tests
"""
from cgitb import reset
import pytest
from release_manager import parse_jira_component
from core.nova_component import NovaComponent, NovaEmptyComponent


class MockComponent:
    """ Mock Jira component """

    def __init__(self, name, description):
        self.name = name
        self.description = description


def test_when_empty_component_provided():
    with pytest.raises(ValueError):
        parse_jira_component(None)


def test_when_component_has_no_description():
    component = MockComponent('component name', None)
    with pytest.raises(ValueError):
        parse_jira_component(component)


def test_when_component_has_no_name():
    component = MockComponent(None, 'component description')
    with pytest.raises(ValueError):
        parse_jira_component(component)


def test_when_component_has_invalid_description():
    component = MockComponent('component name', 'invalid description')
    with pytest.raises(ValueError):
        parse_jira_component(component)


def test_when_component_is_valid():
    component = MockComponent(
        'component name', 'http://github.com/company/project')
    result = parse_jira_component(component)
    assert isinstance(result, NovaComponent)


@pytest.mark.parametrize('component_name', ['n/a', 'N/A', 'N/A ', ' N/A', 'N/A  ', 'n/A', 'N/a', 'n/A ', ' N/a', 'N/a  '])
def test_when_component_is_named_na(component_name):
    component = MockComponent(component_name, '')
    result = parse_jira_component(component)
    assert isinstance(result, NovaEmptyComponent)
    assert result.name == NovaEmptyComponent.default_component_name


def teardown_module():
    """Teardown module"""
    NovaComponent.longest_component_name = 0
