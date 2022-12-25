"""
Nova release tests
"""

import pytest
from core.nova_status import Status as s
from core.nova_release import NovaRelease, get_release_status
from core.nova_component import NovaComponent
from core.nova_task import NovaTask


@pytest.mark.parametrize("component_statuses, expected_status", [
    ([s.UNDEFINED], s.UNDEFINED),
    ([s.UNDEFINED, s.IN_DEVELOPMENT], s.UNDEFINED),
    ([s.UNDEFINED, s.IN_DEVELOPMENT, s.READY_FOR_RELEASE], s.UNDEFINED),
    ([s.UNDEFINED, s.IN_DEVELOPMENT, s.READY_FOR_RELEASE, s.DONE], s.UNDEFINED),
    ([s.IN_DEVELOPMENT, s.READY_FOR_RELEASE, s.DONE], s.IN_DEVELOPMENT),
    ([s.READY_FOR_RELEASE, s.DONE], s.READY_FOR_RELEASE),
    ([s.DONE], s.DONE),
])
def test_release_status(component_statuses, expected_status):
    assert get_release_status(component_statuses) == expected_status


@pytest.mark.parametrize("second_task_status, expected_result", [
    (s.UNDEFINED, False),
    (s.IN_DEVELOPMENT, False),
    (s.READY_FOR_RELEASE, False),
    (s.DONE, True)])
def test_can_release_version(second_task_status: s, expected_result: bool):
    fake_component = NovaComponent('name', None)
    fake_component.add_task(NovaTask('task1', s.DONE))
    fake_component.add_task(NovaTask('task2', second_task_status))

    fake_release = NovaRelease('project1', 'version1', 'delivery1')
    fake_release.add_component(fake_component)

    assert fake_release.can_release_version() is expected_result
