"""
File system helper functions.
"""

import os
import re
import shutil
from enum import Enum
from typing import Optional

import markdown
import pdfkit  # type: ignore

import text_utils as txt


class FilePosition(Enum):
    """
    File position.
    """

    BEGINNING = 0
    END = 1


def search_file_first(root_dir, filename) -> str | None:
    """
    Searches for a file in a directory tree.
    :param root_dir: root directory to start search from
    :param filename: file name to search for
    :return: full path to the first file if found, None otherwise
    """
    for dirpath, _, filenames in os.walk(root_dir):
        for file in filenames:
            if file == filename:
                return os.path.join(dirpath, file)
    return None


def search_files(root_dir, filename) -> list[str]:
    """
    Searches for a file in a directory tree.
    :param root_dir: root directory to start search from
    :param filename: file name to search for
    :return: list of full paths to the files if found, empty list otherwise
    """
    result = []
    for dirpath, _, filenames in os.walk(root_dir):
        for file in filenames:
            if file == filename:
                result.append(os.path.join(dirpath, file))
    return result


def search_changelog_first(root_dir) -> str | None:
    """
    Searches for a changelog file in a directory tree.
    :param root_dir: root directory to start search from
    :return: full path to the first changelog file if found, None otherwise
    """
    return search_file_first(root_dir, "CHANGELOG.md")


def search_changelog_files(root_dir) -> list[str]:
    """
    Searches for changelog files in a directory tree.
    :param root_dir: root directory to start search from
    :return: list of full paths to the changelog files if found, empty list
    otherwise
    """
    return search_files(root_dir, "CHANGELOG.md")


def search_files_with_ext(root_dir, extension):
    """
    Searches for files with a given extension in a directory tree.
    :param root_dir: root directory to start search from
    :param extension: file extension to search for
    :return: list of full paths to the files if found, empty list otherwise
    """
    result = []
    for dirpath, _, filenames in os.walk(root_dir):
        for file in filenames:
            if file.endswith(extension):
                result.append(os.path.join(dirpath, file))
    return result


def search_files_with_content(file_paths, search_string):
    """
    Searches for a string in a list of files.
    :param file_paths: list of file paths to search in
    :param search_string: string to search for
    :return: list of file paths where the string was found
    """
    result = []
    for file_path in file_paths:
        if not os.path.isfile(file_path):
            continue
        with open(file_path, "r", encoding="utf-8") as file_handle:
            if search_string in file_handle.read():
                result.append(file_path)
    return result


def extract_latest_version_from_changelog(changelog_path: str) -> Optional[str]:
    """
    Extracts version from changelog file. The version is expected to be
    the first line in the file. If not, then file will be read line by line
    until the first
    version is found.
    :param changelog_path: path to changelog file
    :return: latest version or None if not found
    """
    with open(changelog_path, "r", encoding="utf-8") as changelog_file:
        for line in changelog_file:
            version = txt.try_extract_nova_component_version(line)
            if version is not None:
                return version
            return None
        return None


def remove_dir(dir_path) -> None:
    """
    Removes a directory tree.
    :param dir_path: path to directory to remove
    """
    if os.path.exists(dir_path):
        shutil.rmtree(dir_path)


def write_file(file_path: str, content: str, position: FilePosition) -> None:
    """
    Writes content to a file. If the file already exists, then the content
    will be inserted at the beginning or at the end of the file. If the file
    does not exist, then it will be created.
    :param file_path: path to the file
    :param content: content to write
    :param position: position to write the content
    """
    mode = "a+" if position == FilePosition.END else "r+"

    try:
        with open(file_path, mode, encoding="utf-8") as file_handle:
            if position == FilePosition.BEGINNING:
                existing_content = file_handle.read()
                file_handle.seek(0, 0)
                file_handle.write(content + existing_content)
            else:
                file_handle.write(content)
    except FileNotFoundError:
        with open(file_path, "w", encoding="utf-8") as file_handle:
            file_handle.write(content)


def replace_in_file(
    file_path: str, search_string: str, replace_string: str
) -> None:
    """
    Replaces a string in a file.
    :param file_path: path to the file
    :param search_string: string to search for, can be a regular expression
    :param replace_string: string to replace with
    """
    if not os.path.isfile(file_path):
        raise FileNotFoundError(f"File {file_path} does not exist")

    if not search_string:
        raise ValueError("Search string cannot be empty")

    if not replace_string:
        raise ValueError("Replace string cannot be empty")

    with open(file_path, "r", encoding="utf-8") as file_handle:
        file_content = file_handle.read()
    file_content = re.sub(search_string, replace_string, file_content)
    with open(file_path, "w", encoding="utf-8") as file_handle:
        file_handle.write(file_content)


def sanitize_filename(filename: str) -> str:
    """
    Sanitizes a file name to make it safe for file system.
    :param filename: file name or folder name to sanitize
    :return: sanitized file or folder name
    """
    if not filename:
        raise ValueError("File name cannot be empty")

    restricted_chars = r'<>:"/\|?*'

    # replace restricted characters with underscore
    filename = re.sub(r"[" + restricted_chars + "]", "_", filename)
    # replace spaces with underscore
    filename = re.sub(r"\s+", "_", filename)
    # finally, remove all characters except alphanumeric, underscore,
    # dot and dash
    return "".join(c for c in filename if c.isalnum() or c in "._- ")


def sanitize_path(path: str) -> str:
    """
    Sanitizes a path to make it safe for file system.
    :param path: path to sanitize
    :return: sanitized path
    """
    if not path:
        raise ValueError("Path cannot be empty")

    parts = path.split(os.path.sep)
    # sanitize each part of the path
    sanitized_parts = [sanitize_filename(part) for part in parts]
    # join sanitized parts back
    return os.path.sep.join(sanitized_parts)


def gen_release_notes_filename(component_name: str, tag_name: str) -> str:
    """
    Generates a release notes file name.
    :param component_name: component name
    :param tag_name: tag name
    :return: release notes file name
    """
    tag_name = re.sub(r"^v|nova-", "", tag_name)
    file_name = f"{component_name.lower()}-{tag_name}"
    return sanitize_filename(file_name)


def markdown_to_pdf(markdown_file_path: str, pdf_file_path: str):
    """
    Converts markdown file to pdf.
    :param markdown_file_path: path to markdown file
    :param pdf_file_path: path to pdf file, if file exists, it will be
    overwritten
    """
    if not os.path.isfile(markdown_file_path):
        raise FileNotFoundError(f"File {markdown_file_path} does not exist")

    if not pdf_file_path:
        raise ValueError("PDF file path cannot be empty")

    with open(markdown_file_path, "r", encoding="utf-8") as file_handle:
        markdown_content = file_handle.read()
    html_content = markdown.markdown(
        markdown_content, extensions=["fenced_code"]
    )
    pdfkit.from_string(html_content, pdf_file_path)


def add_extension(file_path: str, extension: str) -> str:
    """
    Adds an extension to a file path if it does not have one.
    :param file_path: file path
    :param extension: extension to add
    :return: file path with extension
    """
    if not file_path.endswith(extension):
        file_path += extension
    return file_path
