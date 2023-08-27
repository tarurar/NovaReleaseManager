"""
Helper functions for changelog operations.
"""

from packaging.version import InvalidVersion, Version, parse
import fs_utils as fs


def parse_version(changelog_path: str) -> Version:
    """
    Parses the version from the changelog file.

    :param changelog_path: path to the changelog file
    :return: parsed version
    """
    if not changelog_path:
        raise ValueError("Changelog path is not specified")

    version_txt = fs.extract_latest_version_from_changelog(changelog_path)
    if not version_txt:
        raise ValueError(f"Could not extract version from {changelog_path}")

    try:
        return parse(version_txt)
    except InvalidVersion as ex:
        raise ValueError(
            f"Could not parse version from {changelog_path},"
            + " it should be in PEP 440 format"
        ) from ex


def insert_release_notes(changelog_path: str, release_notes: str):
    """
    Inserts the release notes into the changelog file.
    Release flow requires the release notes to be inserted
    into the beginning of changelog file.

    :param changelog_path: path to the changelog file
    :param release_notes: release notes
    """
    if not changelog_path:
        raise ValueError("Changelog path is not specified")

    if not release_notes:
        raise ValueError("Release notes are not specified")

    fs.write_file(
        changelog_path, release_notes + "\n\n", fs.FilePosition.BEGINNING
    )
