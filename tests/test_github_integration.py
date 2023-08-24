"""
Test GitHub integration module.
"""

from datetime import date
import pytest
from core.cvs import CodeRepository, GitCloudService
from core.nova_component import NovaComponent
from core.nova_release import NovaRelease
from integration.github import GitHubIntegration


class FakeGitHub:
    """Fake GitHub API client."""

    def __init__(self):
        pass

    def get_repo(self, _):
        return FakeRepository()


class FakeGitTag:
    """Fake GitHub tag."""

    def __init__(self, tag: str, sha: str):
        self.tag = tag
        self.sha = sha


class FakeGitAuthor:
    """Fake GitHub author."""

    def __init__(self, name: str):
        self.name = name


class FakeGitCommit:
    """Fake GitHub commit."""

    def __init__(self, last_modified: str, author: FakeGitAuthor):
        self.last_modified = last_modified
        self.author = author


class FakeCommit:
    """Fake GitHub commit."""

    def __init__(self, commit: FakeGitCommit):
        self.commit = commit
        self.sha = "fake_sha"


class FakeTag:
    """Fake GitHub tag."""

    def __init__(self, name: str, commit: FakeCommit):
        self.name = name
        self.commit = commit


class FakeBranch:
    """Fake GitHub branch."""

    def __init__(self, commit: FakeCommit, branch_name: str):
        self.commit = commit
        self.branch = branch_name


class FakeGitRelease:
    """Fake GitHub release."""

    def __init__(self, tag: str, name: str, message: str):
        self.tag = tag
        self.name = name
        self.message = message


class FakeRepository:
    """
    Fake GitHub repository.

    Initial tags are created in the range from 1 to 10.
    """

    def __init__(self):
        self.__tags = list(
            map(
                lambda x: FakeTag(
                    str(x),
                    FakeCommit(
                        FakeGitCommit(
                            date.today().strftime("%Y-%m-%d"),
                            FakeGitAuthor(f"Author {x}"),
                        )
                    ),
                ),
                range(1, 11),
            )
        )

    def get_tags(self) -> list[FakeTag]:
        return self.__tags

    def get_branch(self, branch) -> FakeBranch:
        return FakeBranch(
            FakeCommit(FakeGitCommit("", FakeGitAuthor(""))), branch
        )

    def create_git_tag(self, tag_name, _, sha, tag_type) -> FakeGitTag:
        self.__tags.append(
            FakeTag(tag_name, FakeCommit(FakeGitCommit("", FakeGitAuthor(""))))
        )
        return FakeGitTag(tag_name, sha)

    def create_git_ref(self, ref, sha):
        pass

    def create_git_release(self, tag, name, message) -> FakeGitRelease:
        return FakeGitRelease(tag, name, message)


@pytest.fixture(name="fake_input_new_tag_values")
def fixture_fake_input_new_tag_values():
    """
    The sequence of inputs emulates the following user actions:
    1. Empty input to skip tag selection from existing tags.
    2. Enter new name for the tag.
    """
    inputs = ["", "1.0.0"]
    return iter(inputs)


@pytest.fixture(name="fake_input_new_tag_func")
def fixture_fake_input_new_tag_func(fake_input_new_tag_values):
    def fake_input_new_tag(_):
        return next(fake_input_new_tag_values)

    return fake_input_new_tag


@pytest.fixture(name="fake_input_cancel_values")
def fixture_fake_input_cancel_values():
    """
    The sequence of inputs emulates the following user actions:
    1. Empty input to skip tag selection from existing tags.
    2. Cancel tag creation by entering 'q'.
    """
    inputs = ["", "q"]
    return iter(inputs)


@pytest.fixture(name="fake_input_cancel_func")
def fixture_fake_input_cancel_func(fake_input_cancel_values):
    def fake_input_cancel(_):
        return next(fake_input_cancel_values)

    return fake_input_cancel


@pytest.fixture(name="fake_input_second_tag_cancel_values")
def fixture_fake_input_second_tag_cancel_values():
    """
    The sequence of inputs emulates the following user actions:
    1. Select the first tag from the list of existing tags.
    2. Cancel second tag selection by entering empty input.
    """
    inputs = ["1", ""]
    return iter(inputs)


@pytest.fixture(name="fake_input_second_tag_cancel_func")
def fixture_fake_input_second_tag_cancel_func(
    fake_input_second_tag_cancel_values,
):
    def fake_input_second_tag_cancel(_):
        return next(fake_input_second_tag_cancel_values)

    return fake_input_second_tag_cancel


@pytest.fixture(name="fake_github")
def fixture_fake_github():
    return FakeGitHub()


@pytest.fixture(name="integration")
def fixture_integration(fake_github):
    return GitHubIntegration(fake_github)


def test_get_repository_top_tags_default(
    integration: GitHubIntegration,
):
    default_tags_count = 5

    tags = integration.get_repository_top_tags("")
    assert len(tags) == default_tags_count


@pytest.mark.parametrize("tags_count", [1, 2, 3, 4, 5, 6, 7, 8, 9, 10])
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
    monkeypatch, integration: GitHubIntegration, fake_input_new_tag_func
):
    monkeypatch.setattr("builtins.input", fake_input_new_tag_func)
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
