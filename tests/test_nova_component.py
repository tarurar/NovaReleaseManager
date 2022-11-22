"""
Nova component tests
"""

import pytest

from core.nova_component import NovaComponent, NovaEmptyComponent
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


def test_release_notes():
    component = NovaComponent('foo', None)
    component.add_task(NovaTask('key1', 'status1', 'summary1'))
    component.add_task(NovaTask('key2', 'status2', 'summary2'))
    release_notes = component.get_release_notes()

    assert release_notes is not None
    assert 'change log' in release_notes
    assert 'What\'s changed' in release_notes


def test_empty_component_with_default_name_only():
    component = NovaEmptyComponent()
    assert component.name == NovaEmptyComponent.default_component_name


@pytest.mark.parametrize('component_name', ['n/a', 'N/A', 'N/a', 'multiple components'])
def test_empty_component_parses_only_predefined_names(component_name):
    component = NovaEmptyComponent.parse(component_name)
    assert component.name == NovaEmptyComponent.default_component_name


@pytest.mark.parametrize('component_name', ['foo', 'bar', 'baz'])
def test_empty_component_parse_returns_none_for_other_names(component_name):
    component = NovaEmptyComponent.parse(component_name)
    assert component is None
