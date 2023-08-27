"""
Nova task tests
"""

import pytest

from core.nova_status import Status
from core.nova_task import NovaTask


@pytest.mark.parametrize(
    "input_status,expected_status",
    [
        ("whatever", Status.UNDEFINED),
        ("Selected For Release", Status.READY_FOR_RELEASE),
        ("Done", Status.DONE),
        ("In Development", Status.IN_DEVELOPMENT),
        ("Ready for UAT", Status.IN_DEVELOPMENT),
        ("In Testing", Status.IN_DEVELOPMENT),
        ("Ready for Review", Status.IN_DEVELOPMENT),
        ("Ready for testing", Status.IN_DEVELOPMENT),
        ("Open", Status.IN_DEVELOPMENT),
    ],
)
def test_map_jira_issue_status(input_status, expected_status):
    status = NovaTask.map_jira_issue_status(input_status)
    assert status == expected_status


@pytest.mark.parametrize(
    "key,summary,expected",
    [
        ("task1", "summary1", "TASK1: Summary1."),
        ("task2", "summary2.", "TASK2: Summary2."),
        ("task3", "summary3. ", "TASK3: Summary3."),
        ("tAsK4", "summary4.", "TASK4: Summary4."),
        ("Task5", " multiple words summary ", "TASK5: Multiple words summary."),
        ("task6", "[metadata] summary", "TASK6: Summary."),
        ("task7", "[double] [metadata] summary", "TASK7: Summary."),
        (
            "task8",
            "[double][metadata] multiple words",
            "TASK8: Multiple words.",
        ),
        ("task9", "summary9..", "TASK9: Summary9."),
        ("task10", "summary10.. ", "TASK10: Summary10."),
        ("task11", "summary11.. .. ", "TASK11: Summary11.."),
        ("task12", "]summary12.", "TASK12: Summary12."),
        ("task13", "[summary13.", "TASK13: Summary13."),
    ],
)
def test_get_release_notes(key, summary, expected):
    task = NovaTask(key, Status.IN_DEVELOPMENT, summary)
    release_notes = task.get_release_notes()
    lines_count = len(release_notes.split("\n"))

    assert lines_count == 1
    assert release_notes == expected


def test_get_release_notes_asterisk_when_instruction_is_defined():
    task = NovaTask("task", Status.IN_DEVELOPMENT, "summary", "deployment")
    release_notes = task.get_release_notes()

    assert NovaTask.deployment_asterisk in release_notes


def test_create_task_with_empty_name_raises_exception():
    with pytest.raises(ValueError):
        NovaTask("", Status.IN_DEVELOPMENT)
