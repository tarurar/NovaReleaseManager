import pytest

from models.nova_status import Status
from models.nova_task import NovaTask


def test_map_unknown_status():
    status = NovaTask.map_jira_issue_status('whatever')
    assert status == Status.Undefined


def test_map_selected_for_release_status():
    status = NovaTask.map_jira_issue_status('Selected For Release')
    assert status == Status.ReadyForRelease


def test_map_done_status():
    status = NovaTask.map_jira_issue_status('Done')
    assert status == Status.Done


def test_map_in_development_status():
    status = NovaTask.map_jira_issue_status('In Development')
    assert status == Status.InDevelopment
