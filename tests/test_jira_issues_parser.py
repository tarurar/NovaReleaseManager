"""
Jira issues validation tests
"""
import pytest
from release_manager import parse_jira_issue


class MockFields:
    """ Mock Jira issue fields"""

    def __init__(self, components, status_name):
        self.components = components
        self.status = MockStatus(status_name)


class MockStatus:
    """ Mock Jira issue status """

    def __init__(self, name):
        self.name = name


class MockIssue:
    """ Mock Jira issue """

    def __init__(self, key, components, status_name):
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


@pytest.mark.parametrize('issue_key,issue_status',
                         [('issue key', 'Selected For Release')])
def test_when_issue_is_valid(issue_key, issue_status):
    issue = MockIssue(issue_key, ['c1'], issue_status)
    nova_task = parse_jira_issue(issue)
    assert nova_task is not None
