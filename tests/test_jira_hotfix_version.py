"""
"""

from unittest.mock import Mock
import pytest
from jira_utils import is_jira_hotfix_version


@pytest.mark.parametrize(
    "version_name",
    [
        "hotfix-1.0.0",
        "1.0.0-hotfix",
        "1.0.0-hotfix-1",
        "1.0.0-hotfix-2",
        "1.0.0-hotfix-3",
        "1.0.0-HoTfIx-4",
        "hotfiX",
    ],
)
def test_when_version_name_contains_hotfix(version_name):
    version = Mock()
    version.name = version_name
    assert is_jira_hotfix_version(version)
