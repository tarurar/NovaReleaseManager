"""
Nova task tests
"""

import pytest

from core.nova_status import Status
from core.nova_task import NovaTask


def test_map_unknown_status():
    status = NovaTask.map_jira_issue_status('whatever')
    assert status == Status.UNDEFINED


def test_map_selected_for_release_status():
    status = NovaTask.map_jira_issue_status('Selected For Release')
    assert status == Status.READY_FOR_RELEASE


def test_map_done_status():
    status = NovaTask.map_jira_issue_status('Done')
    assert status == Status.DONE


def test_map_in_development_status():
    status = NovaTask.map_jira_issue_status('In Development')
    assert status == Status.IN_DEVELOPMENT


def test_map_in_ready_for_uat_status():
    status = NovaTask.map_jira_issue_status('Ready for UAT')
    assert status == Status.IN_DEVELOPMENT


def test_map_in_testing_status():
    status = NovaTask.map_jira_issue_status('In Testing')
    assert status == Status.IN_DEVELOPMENT


def test_map_ready_for_review_status():
    status = NovaTask.map_jira_issue_status('Ready for Review')
    assert status == Status.IN_DEVELOPMENT


@pytest.mark.parametrize("key,summary,expected", [
    ('task1', 'summary1', 'TASK1: Summary1.'),
    ('task2', 'summary2.', 'TASK2: Summary2.'),
    ('task3', 'summary3. ', 'TASK3: Summary3.'),
    ('tAsK4', 'summary4.', 'TASK4: Summary4.'),
    ('Task5', ' multiple words summary ', 'TASK5: Multiple words summary.'),
    ('task6', '[metadata] summary', 'TASK6: Summary.'),
    ('task7', '[double] [metadata] summary', 'TASK7: Summary.'),
    ('task8', '[double][metadata] multiple words', 'TASK8: Multiple words.'),
    ('task9', 'summary9..', 'TASK9: Summary9.'),
    ('task10', 'summary10.. ', 'TASK10: Summary10.'),
    ('task11', 'summary11.. .. ', 'TASK11: Summary11..'),
    ('task12', ']summary12.', 'TASK12: Summary12.'),
    ('task13', '[summary13.', 'TASK13: Summary13.'),
])
def test_get_release_notes(key, summary, expected):
    task = NovaTask(key, Status.IN_DEVELOPMENT, summary)
    release_notes = task.get_release_notes()
    lines_count = len(release_notes.split('\n'))

    assert lines_count == 1
    assert release_notes == expected
