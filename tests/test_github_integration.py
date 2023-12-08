"""
Test GitHub integration module.
"""

from unittest.mock import Mock

import pytest

from integration.gh import GitHubIntegration


@pytest.fixture(name="mock_config")
def fixture_mock_config():
    mock_config = Mock()
    mock_config.data = {
        "textEditor": "",
        "github": {"username": "", "accessToken": ""},
        "bitbucket": {"username": "", "password": ""},
    }
    return mock_config


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
    monkeypatch, integration: GitHubIntegration, input_cancel
):
    monkeypatch.setattr("builtins.input", input_cancel)
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
