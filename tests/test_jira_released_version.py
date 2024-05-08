"""
This module contains tests for the jira_utils module functions
which are used to work with versions.
"""

from unittest.mock import Mock
from jira_utils import is_jira_released_version


def test_when_version_is_not_released():
    version = Mock()
    version.released = False
    assert not is_jira_released_version(version)


def test_when_version_is_released():
    version = Mock()
    version.released = True
    assert is_jira_released_version(version)
