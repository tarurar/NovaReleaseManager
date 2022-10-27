"""
Jira issues parser tests
"""
import pytest
from release_manager import parse_jira_component
from core.nova_component import NovaComponent


class MockComponent:
    """ Mock Jira component """

    def __init__(self, name, description):
        self.name = name
        self.description = description


def test_when_no_empty_component_provided():
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


def teardown_module():
    """Teardown module"""
    NovaComponent.longest_component_name = 0
