"""
Nova release manager tests
"""

from jira.resources import Version
from release_manager import ReleaseManager


def test_can_release_jira_version_when_version_archived_returns_false():
    version = Version({}, None, {'archived': True})

    assert ReleaseManager.can_release_jira_version(version) is False


def test_can_release_jira_version_when_version_is_released_returns_false():
    version = Version({}, None, {'archived': False, 'released': True})

    assert ReleaseManager.can_release_jira_version(version) is False


def test_can_release_jira_version_when_version_is_not_archived_and_not_released_returns_true():
    version = Version({}, None, {'archived': False, 'released': False})

    assert ReleaseManager.can_release_jira_version(version) is True
