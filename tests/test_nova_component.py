"""
Nova component tests
"""

from core.nova_component import NovaComponent
from core.nova_status import Status
from core.nova_task import NovaTask


def test_longest_name_zero_by_default():
    assert NovaComponent.longest_component_name == 0


def test_longest_name_updated():
    component_name = 'foo'
    NovaComponent(component_name, None)
    assert NovaComponent.longest_component_name == len(component_name)


def test_longest_name_has_longest():
    longest_component_name = 'foo_longest'
    NovaComponent('foo', None)
    NovaComponent(longest_component_name, None)
    assert NovaComponent.longest_component_name == len(longest_component_name)


def test_status_undefined_when_there_are_no_tasks():
    component = NovaComponent('foo', None)
    assert component.get_status() == Status.UNDEFINED


def test_status_undefined_when_single_task_undefined():
    component = NovaComponent('foo', None)
    component.add_task(NovaTask('boo', Status.IN_DEVELOPMENT))
    component.add_task(NovaTask('boo2', Status.UNDEFINED))
    component.add_task(NovaTask('boo3', Status.READY_FOR_RELEASE))
    component.add_task(NovaTask('boo4', Status.DONE))
    assert component.get_status() == Status.UNDEFINED


def test_status_in_development_when_single_task_in_development():
    component = NovaComponent('foo', None)
    component.add_task(NovaTask('boo', Status.IN_DEVELOPMENT))
    component.add_task(NovaTask('boo2', Status.READY_FOR_RELEASE))
    component.add_task(NovaTask('boo3', Status.DONE))
    assert component.get_status() == Status.IN_DEVELOPMENT


def test_status_ready_for_release_only_when_all_tasks_are_ready_for_release():
    component = NovaComponent('foo', None)
    component.add_task(NovaTask('boo', Status.READY_FOR_RELEASE))
    component.add_task(NovaTask('boo2', Status.READY_FOR_RELEASE))
    assert component.get_status() == Status.READY_FOR_RELEASE


def test_status_done_only_when_all_tasks_are_done():
    component = NovaComponent('foo', None)
    component.add_task(NovaTask('boo', Status.DONE))
    component.add_task(NovaTask('boo2', Status.DONE))
    assert component.get_status() == Status.DONE
