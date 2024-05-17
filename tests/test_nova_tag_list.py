"""
Nova Tag List tests
"""

from unittest.mock import Mock
import pytest
from core.nova_component_type import NovaComponentType
from core.nova_tag_list import NovaTagList


@pytest.fixture(name="mock_service")
def fixture_mock_service():
    component = Mock()
    component.ctype = NovaComponentType.SERVICE
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


@pytest.mark.parametrize("mock_tag", package_tag_names(), indirect=True)
def test_try_add_package_tag_to_service(mock_tag, mock_service):
    nova_tag_list = NovaTagList(mock_service)
    assert not nova_tag_list.try_add_tag(mock_tag)


@pytest.mark.parametrize("mock_tag", package_tag_names(), indirect=True)
def test_try_add_package_tag_to_package(mock_tag, mock_package):
    nova_tag_list = NovaTagList(mock_package)
    assert nova_tag_list.try_add_tag(mock_tag)


@pytest.mark.parametrize("mock_tag", package_tag_names(), indirect=True)
def test_try_add_package_tag_to_package_library(mock_tag, mock_package_library):
    nova_tag_list = NovaTagList(mock_package_library)
    assert nova_tag_list.try_add_tag(mock_tag)


@pytest.mark.parametrize("mock_tag", service_tag_names(), indirect=True)
def test_try_add_service_tag_to_service(mock_tag, mock_service):
    nova_tag_list = NovaTagList(mock_service)
    assert nova_tag_list.try_add_tag(mock_tag)


@pytest.mark.parametrize("mock_tag", service_tag_names(), indirect=True)
def test_try_add_service_tag_to_package(mock_tag, mock_package):
    nova_tag_list = NovaTagList(mock_package)
    assert not nova_tag_list.try_add_tag(mock_tag)


# temporarily package library should accept any tags
@pytest.mark.parametrize("mock_tag", library_tag_names(), indirect=True)
def test_try_add_package_library_tag_to_package_library(
    mock_tag, mock_package_library
):
    nova_tag_list = NovaTagList(mock_package_library)
    assert nova_tag_list.try_add_tag(mock_tag)


@pytest.mark.parametrize("mock_tag", service_tag_names(), indirect=True)
def test_try_add_tag_which_already_added(mock_tag, mock_service):
    nova_tag_list = NovaTagList(mock_service)
    assert nova_tag_list.try_add_tag(mock_tag)
    assert not nova_tag_list.try_add_tag(mock_tag)


@pytest.mark.parametrize("mock_tag", library_tag_names(), indirect=True)
def test_try_add_any_tag_to_unknown_component(mock_tag, mock_unknown_component):
    nova_tag_list = NovaTagList(mock_unknown_component)
    assert nova_tag_list.try_add_tag(mock_tag)


def test_from_list_for_service(mock_service):
    original_tags = list(
        map(lambda tag_name: Mock(name=tag_name), service_tag_names())
    )
    nova_tag_list = NovaTagList.from_list(mock_service, original_tags)
    assert len(nova_tag_list) == len(original_tags)
