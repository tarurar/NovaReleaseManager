"""
Jira issues validation tests
"""
import pytest
from jira_utils import parse_jira_issue, filter_jira_issue


class MockedComponent:
    """Mock Jira component"""

    def __init__(self, name):
        self.name = name


class MockedFields:
    """Mock Jira issue fields"""

    def __init__(self, components: list, status_name: str, summary: str):
        self.components = list(map(MockedComponent, components))
        self.status = MockedStatus(status_name)
        self.summary = summary


class MockedStatus:
    """Mock Jira issue status"""

    def __init__(self, name: str):
        self.name = name


class MockedIssue:
    """Mock Jira issue"""

    def __init__(
        self, key: str, components: list, status_name: str, summary: str = ""
    ):
        self.fields = MockedFields(components, status_name, summary)
        self.key = key


class MockedKeylessIssue:
    """Mock Jira issue without key"""

    def __init__(self, components: list, status_name: str, summary: str = ""):
        self.fields = MockedFields(components, status_name, summary)


def test_when_empty_issue_provided():
    with pytest.raises(ValueError):
        parse_jira_issue(None)


@pytest.mark.parametrize("issue_key", ["", None])
def test_when_issue_has_no_key(issue_key):
    issue = MockedIssue(issue_key, ["c1"], "Selected For Release")
    with pytest.raises(ValueError):
        parse_jira_issue(issue)


def test_when_issue_has_no_key_attr():
    issue = MockedKeylessIssue(["c1"], "invalid status")
    with pytest.raises(ValueError):
        parse_jira_issue(issue)


def test_when_issue_has_no_component():
    issue = MockedIssue("issue key", [], "Selected For Release")
    with pytest.raises(ValueError):
        parse_jira_issue(issue)


def test_when_issue_has_more_than_one_component():
    issue = MockedIssue("issue key", ["c1", "c2"], "Selected For Release")
    with pytest.raises(ValueError):
        parse_jira_issue(issue)


def test_when_issue_has_invalid_status():
    issue = MockedIssue("issue key", ["c1"], "invalid status")
    with pytest.raises(ValueError):
        parse_jira_issue(issue)


@pytest.mark.parametrize(
    "issue_key,issue_status", [("issue key", "Selected For Release")]
)
def test_when_issue_is_valid(issue_key, issue_status):
    issue = MockedIssue(issue_key, ["c1"], issue_status)
    nova_task = parse_jira_issue(issue)
    assert nova_task is not None


@pytest.mark.parametrize(
    "jira_cmp_name,nova_cmp_name,expected",
    [
        ("c1", "c1", True),
        ("c1", "c2", False),
        (" c1", "c1 ", True),
        ("C1", "c1", True),
        ("C1", "C1", True),
        (" C1", " c1 ", True),
    ],
)
def test_if_jira_issue_belongs_to_component(
    jira_cmp_name, nova_cmp_name, expected
):
    issue = MockedIssue("issue key", [jira_cmp_name], "Selected For Release")
    result = filter_jira_issue(issue, nova_cmp_name)
    assert result == expected


def test_when_jira_issue_has_no_component():
    issue = MockedIssue("issue key", [], "Selected For Release")
    with pytest.raises(ValueError):
        filter_jira_issue(issue, "c1")
