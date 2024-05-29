"""
Nova Tag List tests
"""

from unittest.mock import Mock
from git import TagReference
import pytest
from core.nova_component_type import NovaComponentType
from core.nova_tag_list import NovaTagList
from integration.git import GitIntegration


@pytest.fixture(name="mock_service")
def fixture_mock_service():
    component = Mock()
    component.ctype = NovaComponentType.SERVICE
    return component


@pytest.fixture(name="mock_service_no_repo")
def fixture_mock_service_no_repo():
    component = Mock()
    component.ctype = NovaComponentType.SERVICE
    component.repo = None
    return component


@pytest.fixture(name="mock_package")
def fixture_mock_package():
    component = Mock()
    component.ctype = NovaComponentType.PACKAGE
    return component


@pytest.fixture(name="mock_package_library")
def fixture_mock_package_library():
    component = Mock()
    component.ctype = NovaComponentType.PACKAGE_LIBRARY
    return component


@pytest.fixture(name="mock_unknown_component")
def fixture_mock_unknown_component():
    component = Mock()
    component.ctype = None
    return component


def package_tag_names():
    return ["contract-1.0.0", "client-1.0.0", "domain-1.0.0"]


def service_tag_names():
    return ["v1.0.0", "nova-1.0.0"]


def library_tag_names():
    return package_tag_names() + service_tag_names() + ["whatever"]


@pytest.fixture(name="mock_tag")
def fixture_mock_tag(request):
    tag = Mock()
    tag.name = request.param
    return tag


@pytest.fixture(name="mock_git_integration")
def fixture_mock_git_integration():
    """
    Mock GitIntegration object with list_tags method
    returning service and package tags
    """
    gi_mock = Mock(spec=GitIntegration)
    service_tag_mock = Mock(spec=TagReference)
    service_tag_mock.name = "v1.0.0"
    package_tag_mock = Mock(spec=TagReference)
    package_tag_mock.name = "client-1.0.0"
    gi_mock.list_tags.return_value = [service_tag_mock, package_tag_mock]
    return gi_mock


@pytest.mark.parametrize("mock_tag", package_tag_names(), indirect=True)
def test_try_add_package_tag_to_service(mock_tag, mock_service):
    nova_tag_list = NovaTagList(mock_service, "")
    assert not nova_tag_list.try_add_tag(mock_tag)


@pytest.mark.parametrize("mock_tag", package_tag_names(), indirect=True)
def test_try_add_package_tag_to_package(mock_tag, mock_package):
    nova_tag_list = NovaTagList(mock_package, "")
    assert nova_tag_list.try_add_tag(mock_tag)


@pytest.mark.parametrize("mock_tag", package_tag_names(), indirect=True)
def test_try_add_package_tag_to_package_library(mock_tag, mock_package_library):
    nova_tag_list = NovaTagList(mock_package_library, "")
    assert nova_tag_list.try_add_tag(mock_tag)


@pytest.mark.parametrize("mock_tag", service_tag_names(), indirect=True)
def test_try_add_service_tag_to_service(mock_tag, mock_service):
    nova_tag_list = NovaTagList(mock_service, "")
    assert nova_tag_list.try_add_tag(mock_tag)


@pytest.mark.parametrize("mock_tag", service_tag_names(), indirect=True)
def test_try_add_service_tag_to_package(mock_tag, mock_package):
    nova_tag_list = NovaTagList(mock_package, "")
    assert not nova_tag_list.try_add_tag(mock_tag)


# temporarily package library should accept any tags
@pytest.mark.parametrize("mock_tag", library_tag_names(), indirect=True)
def test_try_add_package_library_tag_to_package_library(
    mock_tag, mock_package_library
):
    nova_tag_list = NovaTagList(mock_package_library, "")
    assert nova_tag_list.try_add_tag(mock_tag)


@pytest.mark.parametrize("mock_tag", service_tag_names(), indirect=True)
def test_try_add_tag_which_already_added(mock_tag, mock_service):
    nova_tag_list = NovaTagList(mock_service, "")
    assert nova_tag_list.try_add_tag(mock_tag)
    assert not nova_tag_list.try_add_tag(mock_tag)


@pytest.mark.parametrize("mock_tag", library_tag_names(), indirect=True)
def test_try_add_any_tag_to_unknown_component(mock_tag, mock_unknown_component):
    nova_tag_list = NovaTagList(mock_unknown_component, "")
    assert nova_tag_list.try_add_tag(mock_tag)


def test_from_component_no_repo_no_tags(
    mock_service_no_repo, mock_git_integration
):
    nova_tag_list = NovaTagList.from_component(
        mock_service_no_repo, "doesn't matter", mock_git_integration
    )
    assert len(nova_tag_list) == 0


def test_from_component_for_service(mock_service, mock_git_integration):
    nova_tag_list = NovaTagList.from_component(
        mock_service, "doesn't matter", mock_git_integration
    )
    assert len(nova_tag_list) == 1


def test_from_component_for_package(mock_package, mock_git_integration):
    nova_tag_list = NovaTagList.from_component(
        mock_package, "doesn't matter", mock_git_integration
    )
    assert len(nova_tag_list) == 1


@pytest.mark.parametrize(
    "source_tags, filter_value, expected_count",
    [
        (package_tag_names(), "client", 1),
        (package_tag_names(), "ClIeNt", 1),
        (package_tag_names(), "whatever", 0),
        (["client-1", "client-2"], "client", 2),
        ([], "", 0),
        ([], "client", 0),
    ],
)
def test_filter_package_tags(
    mock_package, source_tags, filter_value, expected_count
):
    nova_tag_list = NovaTagList(mock_package, "")
    for tag_name in source_tags:
        tag = Mock()
        tag.name = tag_name
        nova_tag_list.try_add_tag(tag)

    filtered = nova_tag_list.filter(filter_value)
    assert len(filtered) == expected_count
