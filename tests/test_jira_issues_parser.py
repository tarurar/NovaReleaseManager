"""
Jira issues validation tests
"""
import pytest
from release_manager import parse_jira_issue, filter_jira_issue


class MockComponent:
    """Mock Jira component"""

    def __init__(self, name):
        self.name = name


class MockFields:
    """ Mock Jira issue fields"""

    def __init__(self, components: list, status_name: str):
        self.components = list(map(MockComponent, components))
        self.status = MockStatus(status_name)


class MockStatus:
    """ Mock Jira issue status """

    def __init__(self, name: str):
        self.name = name


class MockIssue:
    """ Mock Jira issue """

    def __init__(self, key: str, components: list, status_name: str):
        self.fields = MockFields(components, status_name)
        self.key = key


def test_when_empty_issue_provided():
    with pytest.raises(ValueError):
        parse_jira_issue(None)


@pytest.mark.parametrize('issue_key', ['', None])
def test_when_issue_has_no_key(issue_key):
    issue = MockIssue(issue_key, ['c1'], 'Selected For Release')
    with pytest.raises(ValueError):
        parse_jira_issue(issue)


def test_when_issue_has_no_component():
    issue = MockIssue('issue key', [], 'Selected For Release')
    with pytest.raises(ValueError):
        parse_jira_issue(issue)


def test_when_issue_has_more_than_one_component():
    issue = MockIssue('issue key', ['c1', 'c2'], 'Selected For Release')
    with pytest.raises(ValueError):
        parse_jira_issue(issue)


def test_when_issue_has_invalid_status():
    issue = MockIssue('issue key', ['c1'], 'invalid status')
    with pytest.raises(ValueError):
        parse_jira_issue(issue)


@pytest.mark.parametrize('issue_key,issue_status', [
    ('issue key', 'Selected For Release')])
def test_when_issue_is_valid(issue_key, issue_status):
    issue = MockIssue(issue_key, ['c1'], issue_status)
    nova_task = parse_jira_issue(issue)
    assert nova_task is not None


@pytest.mark.parametrize('jira_cmp_name,nova_cmp_name,expected', [
    ('c1', 'c1', True),
    ('c1', 'c2', False),
    (' c1', 'c1 ', True),
    ('C1', 'c1', True),
    ('C1', 'C1', True),
    (' C1', ' c1 ', True)
])
def test_if_jira_issue_belongs_to_component(
        jira_cmp_name,
        nova_cmp_name,
        expected):
    issue = MockIssue('issue key', [jira_cmp_name], 'Selected For Release')
    result = filter_jira_issue(issue, nova_cmp_name)
    assert result == expected
