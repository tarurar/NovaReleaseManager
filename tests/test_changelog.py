"""
Changelog hepler functions tests.
"""

import os
import shutil
import tempfile
import pytest
import changelog


@pytest.fixture(name="create_test_changelog")
def fixture_create_test_changelog():
    with tempfile.TemporaryDirectory() as root_dir:
        file_path = os.path.join(root_dir, "CHANGELOG.md")
        with open(file_path, "w", encoding="utf-8") as file_handle:
            file_handle.write(
                "## 1.0.0 Nova 2 Delivery 1 (January 1, 2019)\n\n"
                + "### Added\n\n"
                + "- test\n\n"
                + "### Changed\n\n"
                + "- test\n\n"
                + "### Removed\n\n"
                + "- test\n\n"
                + "## 0.1.0 - 2021-01-01\n\n"
                + "### Added\n\n"
                + "- test\n\n"
                + "### Changed\n\n"
                + "- test\n\n"
                + "### Removed\n\n"
                + "- test\n\n"
            )
        yield file_path
        shutil.rmtree(root_dir)


@pytest.fixture(name="create_test_changelog_with_invalid_version")
def fixture_create_test_changelog_with_invalid_version():
    with tempfile.TemporaryDirectory() as root_dir:
        file_path = os.path.join(root_dir, "CHANGELOG.md")
        with open(file_path, "w", encoding="utf-8") as file_handle:
            file_handle.write("## 0. Nova 2 Delivery 1 (January 1, 2019)\n\n")
        yield file_path
        shutil.rmtree(root_dir)


@pytest.fixture(name="create_empty_changelog")
def fixture_create_empty_changelog():
    with tempfile.TemporaryDirectory() as root_dir:
        file_path = os.path.join(root_dir, "CHANGELOG.md")
        with open(file_path, "w", encoding="utf-8") as file_handle:
            file_handle.write("")
        yield file_path
        shutil.rmtree(root_dir)


@pytest.fixture(name="create_test_folder")
def fixture_create_test_folder():
    with tempfile.TemporaryDirectory() as root_dir:
        yield root_dir
        shutil.rmtree(root_dir)


def test_parse_version_raises_exception_when_changelog_path_is_none():
    with pytest.raises(ValueError) as excinfo:
        changelog.parse_version("")

    assert "path is not specified" in str(excinfo.value)


def test_parse_version_raises_exception_when_path_is_not_a_file(
    create_test_folder,
):
    with pytest.raises(ValueError) as excinfo:
        changelog.parse_version(create_test_folder)

    assert "not a file" in str(excinfo.value)


def test_parse_version_raises_exception_when_version_is_not_found(
    create_empty_changelog,
):
    with pytest.raises(ValueError) as excinfo:
        changelog.parse_version(create_empty_changelog)

    assert "Could not extract version" in str(excinfo.value)


def test_parse_version_raises_exception_when_version_invalid(
    create_test_changelog_with_invalid_version,
):
    with pytest.raises(ValueError) as excinfo:
        changelog.parse_version(create_test_changelog_with_invalid_version)

    assert "Could not parse version" in str(excinfo.value)


def test_parse_version_happy_path(create_test_changelog):
    version = changelog.parse_version(create_test_changelog)
    assert str(version) == "1.0.0"


def test_insert_release_notes_raises_exception_when_path_is_empty():
    with pytest.raises(ValueError) as excinfo:
        changelog.insert_release_notes("", "")

    assert "path is not specified" in str(excinfo.value)


def test_insert_release_notes_raises_exception_when_path_is_not_a_file():
    with pytest.raises(ValueError) as excinfo:
        changelog.insert_release_notes("path_is_not_a_file", "")

    assert "not a file" in str(excinfo.value)


def test_insert_release_notes_raises_exception_when_release_notes_is_empty(
    create_test_changelog,
):
    with pytest.raises(ValueError) as excinfo:
        changelog.insert_release_notes(create_test_changelog, "")

    assert "notes are not specified" in str(excinfo.value)


def test_insert_release_notes_happy_path(create_test_changelog):
    changelog.insert_release_notes(create_test_changelog, "test")
    with open(create_test_changelog, "r", encoding="utf-8") as file_handle:
        content = file_handle.read()
        assert content.startswith("test\n\n")
