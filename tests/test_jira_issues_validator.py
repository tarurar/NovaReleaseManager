"""
Jira issues validation tests
"""
from release_manager import validate_jira_issues


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


def test_when_no_issues_found():
    issues = []
    error = validate_jira_issues(issues)
    assert isinstance(error, str)
    assert error != ''


def test_when_issue_has_no_component():
    issues = [MockIssue('issue key', [], 'issue status')]
    error = validate_jira_issues(issues)
    assert isinstance(error, str)
    assert error != ''


def test_when_issue_has_more_than_one_component():
    issues = [MockIssue('issue key', ['c1', 'c2'], 'issue status')]
    error = validate_jira_issues(issues)
    assert isinstance(error, str)
    assert error != ''


def test_when_issue_is_valid():
    issues = [MockIssue('issue key', ['c1'], 'Selected For Release')]
    error = validate_jira_issues(issues)
    assert isinstance(error, str)
    assert error == ''
