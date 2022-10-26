"""
Jira issues validation tests
"""
from release_manager import validate_jira_components


class MockComponent:
    """ Mock Jira component """

    def __init__(self, name, description):
        self.name = name
        self.description = description


def test_when_no_components_found():
    components = []
    error = validate_jira_components(components)
    assert isinstance(error, str)
    assert error != ''


def test_when_component_has_no_description():
    components = [MockComponent('component name', None)]
    error = validate_jira_components(components)
    assert isinstance(error, str)
    assert error != ''


def test_when_component_has_no_name():
    components = [MockComponent(None, 'component description')]
    error = validate_jira_components(components)
    assert isinstance(error, str)
    assert error != ''


def test_when_component_has_invalid_description():
    components = [MockComponent('component name', 'invalid description')]
    error = validate_jira_components(components)
    assert isinstance(error, str)
    assert error != ''


def test_when_component_is_valid():
    components = [MockComponent(
        'component name', 'http://github.com/company/project')]
    error = validate_jira_components(components)
    assert error == ''


def test_when_multiple_components_are_valid_and_invalid():
    components = [
        MockComponent('component name 1', 'http://github.com/company/project'),
        MockComponent('component name 2', 'invalid description')]
    error = validate_jira_components(components)
    assert isinstance(error, str)
    assert 'component name 2' in error
