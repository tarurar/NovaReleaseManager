"""
Nova component tests
"""

from unittest.mock import Mock
import pytest
from packaging.version import InvalidVersion
from core.nova_component_type import NovaComponentType
from core.nova_task import NovaTask
from core.nova_status import Status
from core.nova_component import (
    NovaComponent,
    NovaEmptyComponent,
    get_changelog_url,
    compare_revisions,
    parse_component_type,
)
from core.cvs import GitCloudService, CodeRepository


@pytest.fixture(name="mock_config")
def fixture_mock_config():
    mock_config = Mock()
    mock_config.data = {
        "bitbucket": {"username": "", "password": ""},
    }
    return mock_config


def test_longest_name_zero_by_default():
    assert NovaComponent.longest_component_name == 0


def test_longest_name_updated():
    component_name = "foo"
    NovaComponent(component_name, None)
    assert NovaComponent.longest_component_name == len(component_name)


def test_longest_name_has_longest():
    longest_component_name = "foo_longest"
    NovaComponent("foo", None)
    NovaComponent(longest_component_name, None)
    assert NovaComponent.longest_component_name == len(longest_component_name)


def test_status_undefined_when_there_are_no_tasks():
    component = NovaComponent("foo", None)
    assert component.status == Status.UNDEFINED


def test_status_undefined_when_single_task_undefined():
    component = NovaComponent("foo", None)
    component.add_task(NovaTask("boo", Status.IN_DEVELOPMENT))
    component.add_task(NovaTask("boo2", Status.UNDEFINED))
    component.add_task(NovaTask("boo3", Status.READY_FOR_RELEASE))
    component.add_task(NovaTask("boo4", Status.DONE))
    assert component.status == Status.UNDEFINED


def test_status_in_development_when_single_task_in_development():
    component = NovaComponent("foo", None)
    component.add_task(NovaTask("boo", Status.IN_DEVELOPMENT))
    component.add_task(NovaTask("boo2", Status.READY_FOR_RELEASE))
    component.add_task(NovaTask("boo3", Status.DONE))
    assert component.status == Status.IN_DEVELOPMENT


def test_status_ready_for_release_only_when_all_tasks_are():
    component = NovaComponent("foo", None)
    component.add_task(NovaTask("boo", Status.READY_FOR_RELEASE))
    component.add_task(NovaTask("boo2", Status.READY_FOR_RELEASE))
    assert component.status == Status.READY_FOR_RELEASE


def test_status_ready_for_release_when_all_are_greater_or_equal():
    component = NovaComponent("foo", None)
    component.add_task(NovaTask("boo", Status.READY_FOR_RELEASE))
    component.add_task(NovaTask("boo2", Status.DONE))
    assert component.status == Status.READY_FOR_RELEASE


def test_status_done_only_when_all_tasks_are_done():
    component = NovaComponent("foo", None)
    component.add_task(NovaTask("boo", Status.DONE))
    component.add_task(NovaTask("boo2", Status.DONE))
    assert component.status == Status.DONE


def test_get_release_notes_github(mock_config):
    repo = CodeRepository(
        GitCloudService.GITHUB, "https://example.com", mock_config
    )
    component = NovaComponent("foo", repo)
    component.add_task(NovaTask("key1", Status.READY_FOR_RELEASE, "summary1"))
    component.add_task(NovaTask("key2", Status.READY_FOR_RELEASE, "summary2"))
    release_notes = component.get_release_notes("1", "2")

    assert release_notes
    assert "change log" in release_notes
    assert "What's changed" in release_notes


def test_get_release_notes_empty_changelog_github(mock_config):
    repo = CodeRepository(
        GitCloudService.GITHUB, "https://example.com", mock_config
    )
    component = NovaComponent("boo", repo)
    component.add_task(NovaTask("key1", Status.READY_FOR_RELEASE, "summary1"))
    component.add_task(NovaTask("key2", Status.READY_FOR_RELEASE, "summary2"))
    release_notes = component.get_release_notes(None, None)

    assert release_notes
    assert "change log" not in release_notes


def test_get_release_notes_bitbucket(mock_config):
    repo = CodeRepository(
        GitCloudService.BITBUCKET, "https://example.com", mock_config
    )
    component = NovaComponent("foo", repo)
    component.add_task(NovaTask("key1", Status.READY_FOR_RELEASE, "summary1"))
    component.add_task(NovaTask("key2", Status.READY_FOR_RELEASE, "summary2"))
    release_notes = component.get_release_notes("1", "2")

    assert release_notes is not None
    assert "key1" in release_notes.lower()
    assert "summary2" in release_notes.lower()


@pytest.mark.parametrize(
    "git_cloud,release_notes_empty",
    [
        (GitCloudService.GITHUB, False),
        (GitCloudService.BITBUCKET, False),
        (GitCloudService.UNDEFINED, True),
    ],
)
def test_get_release_notes_are_empty_when_unsupported_git_cloud(
    git_cloud: GitCloudService, release_notes_empty: bool, mock_config
):
    repo = CodeRepository(git_cloud, "https://example.com", mock_config)
    component = NovaComponent("foo", repo)
    component.add_task(NovaTask("key1", Status.IN_DEVELOPMENT, "summary1"))
    component.add_task(NovaTask("key2", Status.IN_DEVELOPMENT, "summary2"))
    release_notes = component.get_release_notes("1", "2")

    assert release_notes_empty == (release_notes == "")


def test_empty_component_with_default_name_only():
    component = NovaEmptyComponent()
    assert component.name == NovaEmptyComponent.default_component_name


@pytest.mark.parametrize(
    "component_name", ["n/a", "N/A", "N/a", "multiple components"]
)
def test_empty_component_parses_only_predefined_names(component_name):
    component = NovaEmptyComponent.parse(component_name)
    assert component is not None
    assert component.name == NovaEmptyComponent.default_component_name


@pytest.mark.parametrize("component_name", ["foo", "bar", "baz"])
def test_empty_component_parse_returns_none_for_other_names(component_name):
    component = NovaEmptyComponent.parse(component_name)
    assert component is None


@pytest.mark.parametrize(
    "revision_from,revision_to,repo_url",
    [
        ("", "", ""),
        ("1", "", ""),
        ("1", "2", ""),
        (" ", " ", " "),
        ("1", " ", " "),
        ("1", "2", " "),
        (None, None, None),
        ("1", None, None),
        ("1", "2", None),
        ("", "2", "url"),
    ],
)
def test_get_changelog_string_when_invalid_parameters(
    revision_from, revision_to, repo_url
):
    result = get_changelog_url(revision_from, revision_to, repo_url)
    assert result == ""


@pytest.mark.parametrize(
    "revision_from,revision_to",
    [("2", "1"), ("v2", "v1"), ("v1.1.1", "v1.1.0")],
)
def test_get_changelog_string_when_revision_from_is_greater(
    revision_from, revision_to
):
    result = get_changelog_url(revision_from, revision_to, "any_url")
    assert result == ""


@pytest.mark.parametrize(
    "revision_from,revision_to,repo_url",
    [
        ("1", "2", "http://example.com"),
        ("1", "2", "http://example.com/"),
        ("1", "2", "http://example.com/any/path"),
        ("v1.9.0", "v1.10.0", "http://example.com/any/path"),
    ],
)
def test_get_changelog_string_happy_path(revision_from, revision_to, repo_url):
    result = get_changelog_url(revision_from, revision_to, repo_url)
    assert result is not None
    assert repo_url in result
    assert revision_from in result
    assert revision_to in result


def test_get_changelog_string_when_url_has_duplicated_slashes():
    url = "http://example.com//"  # double slash
    result = get_changelog_url("1", "2", url)
    assert result is not None
    assert url not in result


@pytest.mark.parametrize(
    "revision_from,revision_to",
    [
        ("2", "1"),
        ("1.1.0", "1.0.0"),
        ("v1.1.0", "v1.0.0"),
        ("1.10.0", "1.9.0"),
        ("v1.10.0", "v1.9.0"),
        ("v1.10.0", "1.9.0"),
        ("1.10.0", "v1.9.0"),
        ("nova-1.10.0", "nova-1.9.0"),
        ("nova-1.10.0", "1.9.0"),
        ("1.10.0", "1.9.0"),
    ],
)
def test_compare_revisions_when_revision_from_is_greater(
    revision_from, revision_to
):
    result = compare_revisions(revision_from, revision_to)
    assert result is False


@pytest.mark.parametrize(
    "revision_from,revision_to",
    [
        ("1", "1"),
        ("1", "1.0"),
        ("1", "1.0.0"),
        ("v1", "1.0"),
        ("v1", "v1.0"),
        ("v1", "v1.0.0"),
        ("0.0.1", "v0.0.1"),
    ],
)
def test_compare_revisions_when_revision_from_is_equal_to_revision_to(
    revision_from, revision_to
):
    result = compare_revisions(revision_from, revision_to)
    assert result is False


@pytest.mark.parametrize(
    "revision_from,revision_to", [(None, "1"), ("1", None), (None, None)]
)
def test_compare_revisions_when_empty_parameters(revision_from, revision_to):
    with pytest.raises(ValueError):
        compare_revisions(revision_from, revision_to)


@pytest.mark.parametrize(
    "revision_from,revision_to", [("qwe", "1"), ("1", "qwe"), ("qwe", "qwe")]
)
def test_compare_revisions_when_invalid_parameters(revision_from, revision_to):
    with pytest.raises(InvalidVersion):
        compare_revisions(revision_from, revision_to)


@pytest.mark.parametrize(
    "component_name,expected_type",
    [
        ("", NovaComponentType.UNDEFINED),
        (None, NovaComponentType.UNDEFINED),
        ("whatever", NovaComponentType.SERVICE),
        ("service", NovaComponentType.SERVICE),
        ("client", NovaComponentType.PACKAGE),
        ("_client", NovaComponentType.PACKAGE),
        ("contracts", NovaComponentType.PACKAGE),
        ("_contracts", NovaComponentType.PACKAGE),
        ("library", NovaComponentType.PACKAGE_LIBRARY),
        ("_library", NovaComponentType.PACKAGE_LIBRARY),
    ],
)
def test_parse_component_type(
    component_name: str, expected_type: NovaComponentType
):
    component_type = parse_component_type(component_name)
    assert component_type == expected_type


def test_component_to_string_returns_name(mock_config):
    component = NovaComponent(
        "foo", CodeRepository(GitCloudService.GITHUB, "url", mock_config)
    )
    assert str(component) == "foo"


def test_component_repr_returns_name(mock_config):
    component = NovaComponent(
        "boo", CodeRepository(GitCloudService.GITHUB, "url", mock_config)
    )
    assert repr(component) == "boo"


def test_tasks_property_returns_tasks(mock_config):
    component = NovaComponent(
        "boo", CodeRepository(GitCloudService.GITHUB, "url", mock_config)
    )
    component.add_task(NovaTask("key1", Status.IN_DEVELOPMENT, "summary1"))
    component.add_task(NovaTask("key2", Status.READY_FOR_RELEASE, "summary2"))
    assert len(component.tasks) == 2
    assert component.tasks[0].name == "key1"
    assert component.tasks[1].name == "key2"


def test_add_tasks_adds_range_of_tasks(mock_config):
    component = NovaComponent(
        "boo", CodeRepository(GitCloudService.GITHUB, "url", mock_config)
    )
    component.add_tasks(
        [
            NovaTask("key1", Status.IN_DEVELOPMENT, "summary1"),
            NovaTask("key2", Status.READY_FOR_RELEASE, "summary2"),
        ]
    )
    assert len(component.tasks) == 2
    assert component.tasks[0].name == "key1"
    assert component.tasks[1].name == "key2"


def test_ctype_property_returns_component_type(mock_config):
    component = NovaComponent(
        "some library",
        CodeRepository(GitCloudService.GITHUB, "url", mock_config),
    )
    assert component.ctype == NovaComponentType.PACKAGE_LIBRARY


def test_describe_status_returns_text_with_3_columns(mock_config):
    component = NovaComponent(
        "some library",
        CodeRepository(GitCloudService.GITHUB, "url", mock_config),
    )
    component.add_tasks(
        [
            NovaTask("key1", Status.IN_DEVELOPMENT, "summary1"),
        ]
    )

    text_status = component.describe_status()

    assert text_status
    assert text_status.count("|") == 2
