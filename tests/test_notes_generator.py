"""
Notes Generator Tests Module
"""

import random
from unittest.mock import MagicMock, Mock, PropertyMock, patch

import pytest
from core.cvs import CodeRepository

from core.nova_component import NovaComponent
from core.nova_release import NovaRelease
from core.nova_status import Status
from integration.git import GitIntegration
from notes_generator import ReleaseNotesGenerator


@pytest.fixture(name="release_not_ready_for_notes")
def fixture_release_not_ready_for_notes():
    release_mock = Mock(spec=NovaRelease)
    release_mock.get_status.return_value = Status.IN_DEVELOPMENT
    return release_mock


@pytest.fixture(name="component_not_ready_for_notes")
def fixture_component_not_ready_for_notes():
    component_mock = Mock(spec=NovaComponent)
    type(component_mock).name = PropertyMock(
        return_value=f"component_{random.randint(1, 1000)}"
    )
    type(component_mock).status = PropertyMock(
        return_value=Status.IN_DEVELOPMENT
    )
    return component_mock


@pytest.fixture(name="component_ready_for_notes")
def fixture_component_ready_for_notes():
    component_mock = Mock(spec=NovaComponent)
    component_mock.repo = Mock(spec=CodeRepository)
    type(component_mock).name = PropertyMock(
        return_value=f"component_{random.randint(1, 1000)}"
    )
    type(component_mock).status = PropertyMock(return_value=Status.DONE)
    return component_mock


@pytest.fixture(name="release_with_component_not_ready_for_notes")
def fixture_release_with_component_not_ready_for_notes(
    component_not_ready_for_notes,
):
    release_mock = MagicMock(
        spec=NovaRelease, name="release_with_component_not_ready_for_notes_mock"
    )
    type(release_mock).version = PropertyMock(return_value="7")
    type(release_mock).delivery = PropertyMock(return_value="77")
    release_mock.get_status.return_value = Status.DONE
    release_mock.__iter__.return_value = [component_not_ready_for_notes]
    return release_mock


@pytest.fixture(name="release_with_component_ready_for_notes")
def fixture_release_with_component_ready_for_notes(
    component_ready_for_notes,
):
    release_mock = MagicMock(spec=NovaRelease)
    type(release_mock).version = PropertyMock(return_value="7")
    type(release_mock).delivery = PropertyMock(return_value="77")
    release_mock.get_status.return_value = Status.DONE
    release_mock.__iter__.return_value = [component_ready_for_notes]
    return release_mock


@pytest.fixture(name="git_integration")
def fixture_git_integration():
    gi_mock = Mock(spec=GitIntegration)
    gi_mock.clone.return_value = "path_to_repo"
    gi_mock.list_tags_with_annotation.return_value = ["1.0.0", "2.0.0"]
    gi_mock.checkout = MagicMock()
    return gi_mock


@pytest.fixture(name="git_integration_no_annotated_tags")
def fixture_git_integration_no_annotated_tags():
    gi_mock = Mock(spec=GitIntegration)
    gi_mock.clone.return_value = "path_to_repo"
    gi_mock.list_tags_with_annotation.return_value = []
    gi_mock.checkout = MagicMock()
    return gi_mock


def test_can_generate_returns_false_when_release_not_ready(
    release_not_ready_for_notes, git_integration
):
    generator = ReleaseNotesGenerator(
        release_not_ready_for_notes, git_integration
    )
    assert not generator.can_generate()


def test_generate_nothing_when_component_not_ready(
    release_with_component_not_ready_for_notes, git_integration
):
    with patch("os.path.exists", return_value=True):
        generator = ReleaseNotesGenerator(
            release_with_component_not_ready_for_notes, git_integration
        )
        notes = generator.generate()
        assert len(notes) == 1
        for _, path in notes.items():
            assert not path


def test_generate_nothing_when_no_annotated_tag(
    release_with_component_ready_for_notes, git_integration_no_annotated_tags
):
    with patch("os.path.exists", return_value=True):
        generator = ReleaseNotesGenerator(
            release_with_component_ready_for_notes,
            git_integration_no_annotated_tags,
        )
        notes = generator.generate()
        assert len(notes) == 1
        for _, path in notes.items():
            assert not path


def test_generate_nothing_when_no_changelog(
    release_with_component_ready_for_notes, git_integration
):
    with patch("os.path.exists", return_value=True), patch(
        "fs_utils.search_changelog", return_value=None
    ):
        generator = ReleaseNotesGenerator(
            release_with_component_ready_for_notes, git_integration
        )
        notes = generator.generate()
        assert len(notes) == 1
        for _, path in notes.items():
            assert not path


def test_generate_happy_path(
    release_with_component_ready_for_notes, git_integration
):
    with patch("os.path.exists", return_value=True), patch(
        "fs_utils.search_changelog", return_value="path_to_changelog"
    ), patch(
        "fs_utils.gen_release_notes_filename",
        return_value="release_notes_filename",
    ), patch(
        "fs_utils.markdown_to_pdf", return_value="path_to_pdf"
    ), patch(
        "os.path.abspath", return_value="absolute_path_to_pdf"
    ):
        generator = ReleaseNotesGenerator(
            release_with_component_ready_for_notes, git_integration
        )
        notes = generator.generate()
        assert len(notes) == 1
        for _, path in notes.items():
            assert path
