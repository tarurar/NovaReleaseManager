"""
Nova task tests
"""

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
