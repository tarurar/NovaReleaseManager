"""
Nova release tests
"""

import pytest
from core.nova_status import Status as s
from core.nova_release import NovaRelease, get_release_status
from core.nova_component import NovaComponent
from core.nova_task import NovaTask


@pytest.mark.parametrize(
    "component_statuses, expected_status",
    [
        ([s.UNDEFINED], s.UNDEFINED),
        ([s.UNDEFINED, s.IN_DEVELOPMENT], s.UNDEFINED),
        ([s.UNDEFINED, s.IN_DEVELOPMENT, s.READY_FOR_RELEASE], s.UNDEFINED),
        (
            [s.UNDEFINED, s.IN_DEVELOPMENT, s.READY_FOR_RELEASE, s.DONE],
            s.UNDEFINED,
        ),
        ([s.IN_DEVELOPMENT, s.READY_FOR_RELEASE, s.DONE], s.IN_DEVELOPMENT),
        ([s.READY_FOR_RELEASE, s.DONE], s.READY_FOR_RELEASE),
        ([s.DONE], s.DONE),
        ([], s.UNDEFINED),
        (None, s.UNDEFINED),
    ],
)
def test_release_status(component_statuses, expected_status):
    assert get_release_status(component_statuses) == expected_status


@pytest.mark.parametrize(
    "second_task_status, expected_result",
    [
        (s.UNDEFINED, False),
        (s.IN_DEVELOPMENT, False),
        (s.READY_FOR_RELEASE, False),
        (s.DONE, True),
    ],
)
def test_can_release_version(second_task_status: s, expected_result: bool):
    fake_component = NovaComponent("name", None)
    fake_component.add_task(NovaTask("task1", s.DONE))
    fake_component.add_task(NovaTask("task2", second_task_status))

    fake_release = NovaRelease("project1", "version1", "delivery1")
    fake_release.add_component(fake_component)

    assert fake_release.can_release_version() is expected_result


def test_get_component_by_name_raises_exception_when_multiple_components_fit():
    fake_component1 = NovaComponent("name1", None)
    fake_component2 = NovaComponent("name2", None)

    sut = NovaRelease("project1", "version1", "delivery1")
    sut.add_component(fake_component1)
    sut.add_component(fake_component2)

    with pytest.raises(Exception):
        sut.get_component_by_name("name")


def test_get_component_by_name_strict_equality():
    fake_component1 = NovaComponent("name1", None)
    fake_component2 = NovaComponent("name12", None)

    sut = NovaRelease("project1", "version1", "delivery1")
    sut.add_component(fake_component1)
    sut.add_component(fake_component2)

    # ensure that we indeed have components with names intersecting
    with pytest.raises(Exception):
        sut.get_component_by_name("name1")

    component = sut.get_component_by_name("name1!")
    assert component == fake_component1


def test_get_component_by_name_strict_equality_special_symbol_used_twice():
    fake_component1 = NovaComponent("!", None)
    fake_component2 = NovaComponent("!1", None)

    sut = NovaRelease("project1", "version1", "delivery1")
    sut.add_component(fake_component1)
    sut.add_component(fake_component2)

    component = sut.get_component_by_name("!")
    assert component is None

    component = sut.get_component_by_name("!!")
    assert component == fake_component1


def test_get_component_by_name_when_no_components_fit():
    sut = NovaRelease("project1", "version1", "delivery1")
    assert sut.get_component_by_name("name") is None


def test_to_string_contains_platform_name():
    sut = NovaRelease("project1", "version1", "delivery1")
    assert "nova" in str(sut).lower()


def test_to_string_contains_delivery():
    sut = NovaRelease("pr1", "v1", "d1")

    normalized = str(sut).lower()
    assert "delivery" in normalized
    assert "d1" in normalized


def test_repr_equals_str():
    sut = NovaRelease("pr1", "v1", "d1")
    assert repr(sut) == str(sut)


def test_project_property_keeps_value():
    sut = NovaRelease("pr1", "v1", "d1")
    assert sut.project == "pr1"


def test_title_property_equals_to_str():
    sut = NovaRelease("pr1", "v1", "d1")
    assert sut.title == str(sut)


def test_describe_status_returns_text():
    fake_component = NovaComponent("name", None)
    fake_component.add_task(NovaTask("task1", s.IN_DEVELOPMENT))
    fake_component.add_task(NovaTask("task2", s.DONE))

    fake_release = NovaRelease("project1", "version1", "delivery1")
    fake_release.add_component(fake_component)

    text_status = fake_release.describe_status()

    assert text_status
