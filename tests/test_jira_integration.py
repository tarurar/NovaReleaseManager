"""
JiraIntegration tests
"""

from jira.resources import Version
from integration.jira import JiraIntegration


def test_can_release_jira_version_when_version_archived_returns_false():
    version = Version({}, None, {'archived': True})
    assert JiraIntegration.can_release_version(version) is False


def test_can_release_jira_version_when_version_is_released_returns_false():
    version = Version({}, None, {'archived': False, 'released': True})
    assert JiraIntegration.can_release_version(version) is False


def test_can_release_jira_version_happy_path():
    version = Version({}, None, {'archived': False, 'released': False})
    assert JiraIntegration.can_release_version(version) is True
