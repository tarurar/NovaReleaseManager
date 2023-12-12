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
    release = Mock(spec=NovaRelease)
    release.get_status.return_value = Status.IN_DEVELOPMENT
    return release


@pytest.fixture(name="component_not_ready_for_notes")
def fixture_component_not_ready_for_notes():
    component = Mock(spec=NovaComponent)
    type(component).name = PropertyMock(
        return_value=f"component_{random.randint(1, 1000)}"
    )
    type(component).status = PropertyMock(return_value=Status.IN_DEVELOPMENT)
    return component


@pytest.fixture(name="component_ready_for_notes")
def fixture_component_ready_for_notes():
    component = Mock(spec=NovaComponent)
    component.repo = Mock(spec=CodeRepository)
    type(component).name = PropertyMock(
        return_value=f"component_{random.randint(1, 1000)}"
    )
    type(component).status = PropertyMock(return_value=Status.DONE)
    return component


@pytest.fixture(name="release_with_component_not_ready_for_notes")
def fixture_release_with_component_not_ready_for_notes(
    component_not_ready_for_notes,
):
    release = MagicMock(
        spec=NovaRelease, name="release_with_component_not_ready_for_notes_mock"
    )
    type(release).version = PropertyMock(return_value="7")
    type(release).delivery = PropertyMock(return_value="77")
    release.get_status.return_value = Status.DONE
    release.__iter__.return_value = [component_not_ready_for_notes]
    return release


@pytest.fixture(name="release_with_component_ready_for_notes")
def fixture_release_with_component_ready_for_notes(
    component_ready_for_notes,
):
    release = MagicMock(spec=NovaRelease)
    type(release).version = PropertyMock(return_value="7")
    type(release).delivery = PropertyMock(return_value="77")
    release.get_status.return_value = Status.DONE
    release.__iter__.return_value = [component_ready_for_notes]
    return release


@pytest.fixture(name="git_integration")
def fixture_git_integration():
    gi = Mock(spec=GitIntegration)
    gi.clone.return_value = "path_to_repo"
    gi.list_tags_with_annotation.return_value = ["1.0.0", "2.0.0"]
    gi.checkout = MagicMock()
    return gi


@pytest.fixture(name="git_integration_no_annotated_tags")
def fixture_git_integration_no_annotated_tags():
    gi = Mock(spec=GitIntegration)
    gi.clone.return_value = "path_to_repo"
    gi.list_tags_with_annotation.return_value = []
    gi.checkout = MagicMock()
    return gi


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
