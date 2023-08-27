"""
Jira issues validation tests
"""
from collections import namedtuple
import pytest
from jira_utils import parse_jira_issue, filter_jira_issue

FakeComponent = namedtuple("FakeComponent", ["name"])
FakeStatus = namedtuple("FakeStatus", ["name"])
FakeFields = namedtuple("FakeFields", ["components", "status", "summary"])
FakeIssue = namedtuple("FakeIssue", ["fields", "key"])
FakeKeyLessIssue = namedtuple("FakeKeyLessIssue", ["fields"])


@pytest.mark.parametrize("issue_key", ["", None])
def test_when_issue_has_no_key(issue_key):
    issue = FakeIssue(
        FakeFields(
            [FakeComponent("c1")], FakeStatus("Selected For Release"), ""
        ),
        issue_key,
    )
    with pytest.raises(ValueError):
        parse_jira_issue(issue)  # type: ignore


def test_when_issue_has_no_key_attr():
    issue = FakeKeyLessIssue(
        FakeFields([FakeComponent("c1")], FakeStatus("invalid status"), "")
    )
    with pytest.raises(ValueError):
        parse_jira_issue(issue)  # type: ignore


def test_when_issue_has_no_component():
    issue = FakeIssue(
        FakeFields([], FakeStatus("Selected For Release"), ""), "issue key"
    )
    with pytest.raises(ValueError):
        parse_jira_issue(issue)  # type: ignore


def test_when_issue_has_more_than_one_component():
    issue = FakeIssue(
        FakeFields(
            [FakeComponent("c1"), FakeComponent("c2")],
            FakeStatus("Selected For Release"),
            "",
        ),
        "issue key",
    )
    with pytest.raises(ValueError):
        parse_jira_issue(issue)  # type: ignore


def test_when_issue_has_invalid_status():
    issue = FakeIssue(
        FakeFields([FakeComponent("c1")], FakeStatus("invalid status"), ""),
        "issue key",
    )
    with pytest.raises(ValueError):
        parse_jira_issue(issue)  # type: ignore


@pytest.mark.parametrize(
    "issue_key,issue_status", [("issue key", "Selected For Release")]
)
def test_when_issue_is_valid(issue_key, issue_status):
    issue = FakeIssue(
        FakeFields([FakeComponent("c1")], FakeStatus(issue_status), ""),
        issue_key,
    )
    nova_task = parse_jira_issue(issue)  # type: ignore
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
    issue = FakeIssue(
        FakeFields(
            [FakeComponent(jira_cmp_name)],
            FakeStatus("Selected For Release"),
            "",
        ),
        "issue key",
    )
    result = filter_jira_issue(issue, nova_cmp_name)
    assert result == expected


def test_when_jira_issue_has_no_component():
    issue = FakeIssue(
        FakeFields([], FakeStatus("Selected For Release"), ""), "issue key"
    )
    with pytest.raises(ValueError):
        filter_jira_issue(issue, "c1")
