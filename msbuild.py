"""
Helper functions for building with MSBuild.
"""

from packaging.version import Version
import fs_utils as fs


def update_project_version(file_path: str, version: Version):
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
        update_project_version(csproj_file_path, version)
