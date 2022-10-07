import pytest

from models.nova_component import NovaComponent
from models.nova_status import Status
from models.nova_task import NovaTask


def test_longest_name_zero_by_default():
    assert NovaComponent.longest_name == 0


def test_longest_name_updated():
    component_name = 'foo'
    NovaComponent(component_name)
    assert NovaComponent.longest_name == len(component_name)


def test_longest_name_has_longest():
    longest_component_name = 'foo_longest'
    NovaComponent('foo')
    NovaComponent(longest_component_name)
    assert NovaComponent.longest_name == len(longest_component_name)


def test_status_undefined_when_there_are_no_tasks():
    component = NovaComponent('foo')
    assert component.get_status() == Status.Undefined


def test_status_undefined_when_single_task_undefined():
    component = NovaComponent('foo')
    component.add_task(NovaTask('boo', Status.InDevelopment))
    component.add_task(NovaTask('boo2', Status.Undefined))
    component.add_task(NovaTask('boo3', Status.ReadyForRelease))
    component.add_task(NovaTask('boo4', Status.Done))
    assert component.get_status() == Status.Undefined


def test_status_in_development_when_single_task_in_development():
    component = NovaComponent('foo')
    component.add_task(NovaTask('boo', Status.InDevelopment))
    component.add_task(NovaTask('boo2', Status.ReadyForRelease))
    component.add_task(NovaTask('boo3', Status.Done))
    assert component.get_status() == Status.InDevelopment


def test_status_ready_for_release_only_when_all_tasks_are_ready_for_release():
    component = NovaComponent('foo')
    component.add_task(NovaTask('boo', Status.ReadyForRelease))
    component.add_task(NovaTask('boo2', Status.ReadyForRelease))
    assert component.get_status() == Status.ReadyForRelease


def test_status_done_only_when_all_tasks_are_done():
    component = NovaComponent('foo')
    component.add_task(NovaTask('boo', Status.Done))
    component.add_task(NovaTask('boo2', Status.Done))
    assert component.get_status() == Status.Done
