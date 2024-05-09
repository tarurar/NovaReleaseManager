"""
Notes Generator Module
"""

import os
from typing import Optional
from config import Config
from core.nova_component import NovaComponent
from core.nova_release import NovaRelease
from core.nova_status import Status

import fs_utils as fs
from integration.git import GitIntegration


class NotesGenerator:
    """
    Responsible for generating release notes for a given release.
    Can be reused to generate release notes in different formats, for this
    purpose, the generator should be subclassed and the __convert method
    should be overridden.
    Release notes are taken from the CHANGELOG.md file in the component's
    repository. The tag to generate release notes for is determined by the
    release title.
    """

    class Result:
        """
        Represents the result of release notes generation
        for a single component.
        Either path or error should be set, but not both.
        """

        def __init__(self, path=None, error=None):
            if (path is None) and (error is None):
                raise ValueError("Either path or error should be set")
            if path and error:
                raise ValueError(
                    "Either path or error should be set, but not both"
                )
            self._path = path
            self._error = error

        @property
        def path(self):
            return self._path

        @property
        def error(self):
            return self._error

        @staticmethod
        def from_path(path: str):
            return NotesGenerator.Result(path=path)

        @staticmethod
        def from_error(error: str):
            return NotesGenerator.Result(error=error)

        @staticmethod
        def from_exception(e: Exception):
            return NotesGenerator.Result.from_error(str(e))

    def __init__(
        self, release: NovaRelease, gi: GitIntegration, config=None
    ) -> None:
        if config is None:
            config = Config()

        self.__release = release
        self.__gi = gi

        # todo: probably, path sanitization should be moved inside
        # the Config class because the path can be used by other
        # classes as well
        output_path = config.get_artifacts_folder_path(
            self.__release.version, self.__release.delivery, ""
        )
        self.__output_path = fs.sanitize_path(output_path)

    def __ensure_output_folder_exists(self) -> None:
        """
        Ensures the output folder exists or creates it if not.
        """
        if not os.path.exists(self.__output_path):
            os.makedirs(self.__output_path)

    def __convert_changelog_to_notes(self, component: NovaComponent) -> str:
        """
        Generates release notes for a single component.

        :param component: component to generate release notes for
        :return: path to the release notes file
        """
        assert component.repo is not None

        sources_dir = self.__gi.clone(component.repo.url)
        release_tag = self.__find_release_tag(sources_dir)
        if release_tag is None:
            raise ValueError("No tag found for the release")

        changelog_path = self.__find_changelog_at_tag(sources_dir, release_tag)
        if not changelog_path:
            raise ValueError(f"CHANGELOG.md not found at the tag {release_tag}")

        notes_file_path = self.__gen_notes_file_path(component, release_tag)
        return self.__convert(changelog_path, notes_file_path)

    def __gen_notes_file_path(
        self, component: NovaComponent, tag_name: str
    ) -> str:
        """
        Generates the file name for the release notes file.

        :param component: component to generate release notes for
        :param tag_name: tag name
        :return: path to the release notes file
        """
        filename = fs.gen_release_notes_filename(component.name, tag_name)
        return f"{self.__output_path}/{filename}"

    def __find_changelog_at_tag(
        self, sources_dir: str, tag_name: str
    ) -> Optional[str]:
        """
        Finds the changelog file at the specified tag.

        :param sources_dir: path to the sources directory
        :param tag_name: tag name
        :return: path to the changelog file or None if not found
        """
        self.__gi.checkout(sources_dir, tag_name)
        return fs.search_changelog(sources_dir)

    def __find_release_tag(self, sources_dir: str) -> Optional[str]:
        """
        Finds the tag name with the annotation after
        the release title.

        :param sources_dir: path to the sources directory
        :return: tag name or None if not found
        """
        annotated_tags = self.__gi.list_tags_with_annotation(
            sources_dir, self.__release.title
        )
        return None if not annotated_tags else annotated_tags[0]

    def __convert(self, markdown_path: str, output_path: str) -> str:
        """
        Converts markdown to PDF.

        :param markdown_path: path to the markdown file
        :param output_path: path to the output PDF file
        :return: path to the output PDF file
        """
        output_path = fs.add_extension(output_path, ".pdf")
        fs.markdown_to_pdf(markdown_path, output_path)

        return output_path

    def can_generate(self) -> bool:
        """
        Checks if the generator can generate release notes
        for a given release based on its status.
        """
        return self.__release.get_status() == Status.DONE

    def generate(
        self,
    ) -> dict[str, Result]:
        """
        Generates release notes for a given release.

        :return: dictionary with component name as a key and result
        object as a value for each component with absolute path to the
        release notes file
        """
        self.__ensure_output_folder_exists()

        result = {}
        for component in self.__release:
            notes_file_path = None
            try:
                notes_file_path = self.__convert_changelog_to_notes(component)
            except Exception as e:
                result[component.name] = NotesGenerator.Result.from_exception(e)
                continue

            absolute_path = os.path.abspath(notes_file_path)
            result[component.name] = NotesGenerator.Result.from_path(
                absolute_path
            )

        return result
