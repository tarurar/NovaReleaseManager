"""
The module describes the component release flow for the
Bitbucket hosted repositories.
"""

from packaging.version import InvalidVersion, Version, parse
import fs_utils as fs


def parse_version_from_changelog(changelog_path: str) -> Version:
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
    Bitbucket release flow requires the release notes to be inserted
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


def update_cs_project_version(file_path: str, version: Version):
    """
    Updates the project version tag in the specified file.
    """
    if not file_path:
        raise ValueError("File path is not specified")

    if version is None:
        raise ValueError("Version is not specified")

    fs.replace_in_file(
        file_path, r"<Version>(.*?)<\/Version>", f"<Version>{version}</Version>"
    )


def update_solution_version(sources_dir: str, version: Version):
    """
    Searches for *.csproj files in sources_dir and updates
    version tag in each file.
    """

    if not sources_dir:
        raise ValueError("Sources directory is not specified")

    if version is None:
        raise ValueError("Version is not specified")

    csproj_file_paths = fs.search_files_with_ext(sources_dir, "csproj")
    if not csproj_file_paths:
        raise FileNotFoundError(
            "Could not find any *.csproj files in " + f"{sources_dir}"
        )

    for csproj_file_path in csproj_file_paths:
        update_cs_project_version(csproj_file_path, version)
