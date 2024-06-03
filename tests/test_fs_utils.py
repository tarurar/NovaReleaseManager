"""
File system helper function tests
"""

import tempfile
import os
import shutil
import pytest
import fs_utils as fs


def read_file(file_path):
    with open(file_path, "r", encoding="utf-8") as file_handle:
        return file_handle.read()


@pytest.fixture(name="create_test_files")
def fixture_create_test_files():
    with tempfile.TemporaryDirectory() as root_dir:
        sub_dir = os.path.join(root_dir, "subdir")
        os.mkdir(sub_dir)
        file_path_1 = os.path.join(sub_dir, "test_file_1.txt")
        with open(file_path_1, "w", encoding="utf-8") as file_handle:
            file_handle.write("test")
        file_path_2 = os.path.join(sub_dir, "test_file_2.txt")
        with open(file_path_2, "w", encoding="utf-8") as file_handle:
            file_handle.write("test")
        yield root_dir, sub_dir, file_path_1, file_path_2
        shutil.rmtree(root_dir)


@pytest.fixture(name="create_test_files_ext")
def fixture_create_test_files_ext():
    with tempfile.TemporaryDirectory() as root_dir:
        sub_dir = os.path.join(root_dir, "subdir")
        os.mkdir(sub_dir)
        file_path_1 = os.path.join(sub_dir, "test_file_1.txt")
        with open(file_path_1, "w", encoding="utf-8") as file_handle:
            file_handle.write("test")
        file_path_2 = os.path.join(sub_dir, "test_file_2.doc")
        with open(file_path_2, "w", encoding="utf-8") as file_handle:
            file_handle.write("test")
        file_path_3 = os.path.join(sub_dir, "test_file_3.txt")
        with open(file_path_3, "w", encoding="utf-8") as file_handle:
            file_handle.write("test")
        yield root_dir, sub_dir, file_path_1, file_path_2, file_path_3
        shutil.rmtree(root_dir)


@pytest.fixture(name="create_test_files_content")
def fixture_create_test_files_content():
    with tempfile.TemporaryDirectory() as root_dir:
        file_path_1 = os.path.join(root_dir, "test_file_1.txt")
        with open(file_path_1, "w", encoding="utf-8") as file_handle:
            file_handle.write("this is a test\nline 2\nline 3")
        file_path_2 = os.path.join(root_dir, "test_file_2.txt")
        with open(file_path_2, "w", encoding="utf-8") as file_handle:
            file_handle.write(
                "another test\nwith some example text\nand more lines"
            )
        file_path_3 = os.path.join(root_dir, "test_file_3.txt")
        with open(file_path_3, "w", encoding="utf-8") as file_handle:
            file_handle.write("no matches\nin this file")
        yield [file_path_1, file_path_2, file_path_3], root_dir
        shutil.rmtree(root_dir)


@pytest.fixture(name="create_invalid_changelog_file")
def fixture_create_invalid_changelog_file():
    with tempfile.TemporaryDirectory() as root_dir:
        file_path = os.path.join(root_dir, "CHANGELOG.md")
        with open(file_path, "w", encoding="utf-8") as file_handle:
            file_handle.write("this is not a valid changelog file")
        yield file_path
        shutil.rmtree(root_dir)


@pytest.fixture(name="create_valid_changelog_file")
def fixture_create_valid_changelog_file():
    with tempfile.TemporaryDirectory() as root_dir:
        file_path = os.path.join(root_dir, "CHANGELOG.md")
        with open(file_path, "w", encoding="utf-8") as file_handle:
            file_handle.write("## 1.0.0 Nova 2 Delivery 1 (January 1, 2019)")
        yield file_path
        shutil.rmtree(root_dir)


@pytest.fixture(name="create_test_file_for_replacement")
def fixture_create_test_file_for_replacement():
    with tempfile.NamedTemporaryFile() as file_handle:
        file_handle.write(b"text to replace")
        file_handle.flush()
        yield file_handle.name


def test_search_file_first_found(create_test_files):
    root_dir, _, file_path_1, _ = create_test_files
    assert fs.search_file_first(root_dir, "test_file_1.txt") == file_path_1


def test_search_file_first_not_found(create_test_files):
    root_dir, _, _, _ = create_test_files
    assert fs.search_file_first(root_dir, "nonexistent_file.txt") is None


def test_search_file_first_ignore_directories(create_test_files):
    root_dir, sub_dir, _, _ = create_test_files
    assert fs.search_file_first(root_dir, "subdir") != sub_dir


def test_search_files_found(create_test_files):
    root_dir, _, file_path_1, _ = create_test_files
    result = fs.search_files(root_dir, "test_file_1.txt")
    assert len(result) == 1
    assert result[0] == file_path_1


def test_search_files_not_found(create_test_files):
    root_dir, _, _, _ = create_test_files
    assert not fs.search_files(root_dir, "nonexistent_file.txt")


def test_search_files_ignore_directories(create_test_files):
    root_dir, sub_dir, _, _ = create_test_files
    assert not fs.search_files(root_dir, "subdir")


def test_search_files_with_ext(create_test_files_ext):
    (
        root_dir,
        sub_dir,
        file_path_1,
        file_path_2,
        file_path_3,
    ) = create_test_files_ext
    assert set(fs.search_files_with_ext(root_dir, ".txt")) == set(
        [file_path_1, file_path_3]
    )
    assert set(fs.search_files_with_ext(sub_dir, ".doc")) == set([file_path_2])


def test_search_files_with_ext_no_files_found(create_test_files_ext):
    (
        root_dir,
        _,
        _,
        _,
        _,
    ) = create_test_files_ext
    assert not fs.search_files_with_ext(root_dir, ".md")


def test_search_files_with_content(create_test_files_content):
    file_paths, root_dir = create_test_files_content
    assert set(fs.search_files_with_content(file_paths, "example")) == set(
        [os.path.join(root_dir, "test_file_2.txt")]
    )
    assert set(fs.search_files_with_content(file_paths, "test")) == set(
        [
            os.path.join(root_dir, "test_file_1.txt"),
            os.path.join(root_dir, "test_file_2.txt"),
        ]
    )


def test_search_files_with_content_skips_directories(create_test_files_content):
    _, root_dir = create_test_files_content
    assert not fs.search_files_with_content(root_dir, "whatever")


def test_no_test_search_files_with_content_not_found(create_test_files_content):
    file_paths, _ = create_test_files_content
    assert not fs.search_files_with_content(file_paths, "not_found")


def test_write_to_non_existing_file():
    with tempfile.NamedTemporaryFile() as file_handle:
        # ensure file is deleted
        os.unlink(file_handle.name)

        fs.write_file(file_handle.name, "test", fs.FilePosition.BEGINNING)
        content = read_file(file_handle.name)

        assert content == "test"


def test_write_to_beginning_of_file():
    with tempfile.NamedTemporaryFile() as file_handle:
        file_handle.write(b"existing content")
        file_handle.flush()

        fs.write_file(file_handle.name, "test", fs.FilePosition.BEGINNING)
        content = read_file(file_handle.name)

        assert content == "testexisting content"


def test_write_to_end_of_file():
    with tempfile.NamedTemporaryFile() as file_handle:
        file_handle.write(b"existing content")
        file_handle.flush()

        fs.write_file(file_handle.name, "test", fs.FilePosition.END)
        content = read_file(file_handle.name)

        assert content == "existing contenttest"


def test_extract_latest_version_from_changelog_invalid(
    create_invalid_changelog_file,
):
    file_path = create_invalid_changelog_file
    version = fs.extract_latest_version_from_changelog(file_path)
    assert version is None


def test_extract_latest_version_from_changelog_valid(
    create_valid_changelog_file,
):
    file_path = create_valid_changelog_file
    version = fs.extract_latest_version_from_changelog(file_path)
    assert version


def test_replace_in_file_raises_exception_if_file_does_not_exist():
    with pytest.raises(FileNotFoundError):
        fs.replace_in_file("not_existing_file_name", "test", "test2")


def test_replace_in_file_raises_exception_if_file_is_not_a_file():
    with tempfile.TemporaryDirectory() as root_dir:
        file_path = os.path.join(root_dir, "test_file")
        os.mkdir(file_path)
        with pytest.raises(FileNotFoundError):
            fs.replace_in_file(file_path, "test", "test2")


def test_replace_in_file_raises_exception_when_search_string_is_empty():
    with tempfile.NamedTemporaryFile() as file_handle:
        with pytest.raises(ValueError):
            fs.replace_in_file(file_handle.name, "", "test2")


def test_replace_in_file_raises_exception_when_replace_string_is_empty():
    with tempfile.NamedTemporaryFile() as file_handle:
        with pytest.raises(ValueError):
            fs.replace_in_file(file_handle.name, "test", "")


def test_replace_in_file_replaces_text(create_test_file_for_replacement):
    file_path = create_test_file_for_replacement
    fs.replace_in_file(file_path, "text to replace", "replacement")
    content = read_file(file_path)
    assert content == "replacement"


def test_sanitize_filename_raises_exception_when_filename_is_empty():
    with pytest.raises(ValueError):
        fs.sanitize_filename("")


def test_sanitize_filename_remove_restricted_characters():
    assert fs.sanitize_filename("test<file>name?*") == "test_file_name__"


def test_sanitize_filename_replace_spaces_with_underscore():
    assert fs.sanitize_filename("test file name") == "test_file_name"


def test_sanitize_filename_preserve_alphanumeric_underscore_dot_dash():
    assert fs.sanitize_filename("test-file_name.123") == "test-file_name.123"


def test_sanitize_filename_remove_leading_and_trailing_spaces():
    assert fs.sanitize_filename("  testfile  ") == "_testfile_"


def test_sanitize_filename_string_with_only_restricted_chars():
    assert fs.sanitize_filename('<>:"/\\|?*') == "________"


def test_sanitize_filename_string_with_mixed_characters():
    assert fs.sanitize_filename("file<name>: 123") == "file_name___123"


def test_gen_release_notes_filename_removes_v_prefix():
    assert (
        fs.gen_release_notes_filename("component1", "v1.0.0")
        == "component1-1.0.0"
    )


def test_gen_release_notes_filename_removes_nova_prefix():
    assert (
        fs.gen_release_notes_filename("component1", "nova-1.0.0")
        == "component1-1.0.0"
    )


def test_add_extension_adds_extension():
    assert fs.add_extension("test", ".txt") == "test.txt"


def test_add_extension_does_not_add_extension_if_already_present():
    assert fs.add_extension("test.txt", ".txt") == "test.txt"


def test_sanitize_path_raises_exception_when_path_is_empty():
    with pytest.raises(ValueError):
        fs.sanitize_path("")


def test_sanitize_path():
    assert fs.sanitize_path("test/path") == "test/path"


def test_sanotize_path_removes_restricted_characters():
    assert fs.sanitize_path("test/path1<>/path2*") == "test/path1__/path2_"
