"""
Test GitHub integration module.
"""

import pytest
from core.cvs import CodeRepository, GitCloudService
from core.nova_component import NovaComponent
from core.nova_release import NovaRelease
from integration.github import GitHubIntegration
from tests.fakes import FakeConfig


def test_get_repository_top_tags_default(
    integration: GitHubIntegration,
):
    default_tags_count = 5

    tags = integration.get_repository_top_tags("")
    assert len(tags) == default_tags_count


@pytest.mark.parametrize("tags_count", [1, 2, 3, 4, 5])
def test_get_repository_top_tags(integration: GitHubIntegration, tags_count):
    tags = integration.get_repository_top_tags("repo_url", tags_count)
    assert len(tags) == tags_count


def test_create_tag_returns_created_tag(integration: GitHubIntegration):
    name = "new_tag"
    tag = integration.create_tag("repo_url", "message", name)
    assert tag.name == name


@pytest.mark.parametrize("existing_tag_selection", [1, 2, 3, 4, 5])
def test_select_or_create_tag_returns_existing_tag(
    monkeypatch, integration: GitHubIntegration, existing_tag_selection
):
    monkeypatch.setattr("builtins.input", lambda _: str(existing_tag_selection))
    tag = integration.select_or_create_tag("repo_url", "message")

    assert tag
    assert tag.name == str(existing_tag_selection)


def test_select_or_create_tag_returns_created_tag(
    monkeypatch, integration: GitHubIntegration, input_new_tag
):
    monkeypatch.setattr("builtins.input", input_new_tag)
    tag = integration.select_or_create_tag("repo_url", "message")

    assert tag
    assert tag.name == "1.0.0"


def test_select_or_create_tag_returns_none(
    monkeypatch, integration: GitHubIntegration, fake_input_cancel_func
):
    monkeypatch.setattr("builtins.input", fake_input_cancel_func)
    tag = integration.select_or_create_tag("repo_url", "message")

    assert tag is None


@pytest.mark.parametrize("existing_tag_selection", [1, 2, 3, 4, 5])
def test_select_or_autodetect_tag_returns_existing_tag(
    monkeypatch, integration: GitHubIntegration, existing_tag_selection
):
    monkeypatch.setattr("builtins.input", lambda _: str(existing_tag_selection))
    tag = integration.select_or_autodetect_tag("repo_url", [])

    assert tag
    assert tag.name == str(existing_tag_selection)


@pytest.mark.parametrize(
    "exclude_tag_list, expected_tag",
    [
        ([], "1"),
        (["1"], "2"),
        (["1", "4"], "2"),
        (["1", "2", "3"], "4"),
        (["1", "2", "3", "4", "5"], None),
    ],
)
def test_select_or_autodetect_returns_autodetected_tag(
    monkeypatch, integration: GitHubIntegration, exclude_tag_list, expected_tag
):
    # emulate skipping tag selection
    monkeypatch.setattr("builtins.input", lambda _: "")
    tag = integration.select_or_autodetect_tag("repo_url", exclude_tag_list)

    if expected_tag:
        assert tag
        assert tag.name == expected_tag
    else:
        assert tag is None


def test_create_git_release_if_tag_not_selected_returns_none(
    monkeypatch, integration: GitHubIntegration, fake_input_cancel_func
):
    monkeypatch.setattr("builtins.input", fake_input_cancel_func)
    release = integration.create_git_release(
        NovaRelease("project", "version", "delivery"),
        NovaComponent("component", CodeRepository(GitCloudService.GITHUB, "")),
    )

    assert release is None


@pytest.mark.parametrize("fake_config", [FakeConfig(1)], indirect=True)
def test_create_git_release_if_previous_tag_not_selected_returns_none(
    monkeypatch,
    integration: GitHubIntegration,
    fake_input_second_tag_cancel_func,
):
    """
    Here the original FakeConfig fixture is replaced with the one that provides
    only one tag. This is done to emulate the situation when there is only one
    tag in the repository and the user cancels the selection of the second tag.
    Autoselection of the second tag is not possible in this case. So, the
    create_git_release() method should return None.
    """
    monkeypatch.setattr("builtins.input", fake_input_second_tag_cancel_func)
    release = integration.create_git_release(
        NovaRelease("project", "version", "delivery"),
        NovaComponent("component", CodeRepository(GitCloudService.GITHUB, "")),
    )

    assert release is None


@pytest.mark.parametrize(
    "fake_config", [FakeConfig(create_release=False)], indirect=True
)
def test_create_git_release_raises_exception_if_release_not_created(
    monkeypatch, integration: GitHubIntegration, fake_input_both_tags_func
):
    """
    Here the original FakeConfig fixture is replaced with the one that
    prevents the creation of the release. This is done to emulate the situation
    when the user selects two tags and the release is not created for some
    reason. The create_git_release() method should raise an exception.
    """
    monkeypatch.setattr("builtins.input", fake_input_both_tags_func)
    with pytest.raises(IOError):
        integration.create_git_release(
            NovaRelease("project", "version", "delivery"),
            NovaComponent(
                "component", CodeRepository(GitCloudService.GITHUB, "")
            ),
        )
