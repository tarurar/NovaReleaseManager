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


class ReleaseNotesGenerator:
    """
    Responsible for generating release notes for a given release.
    Can be reused to generate release notes in different formats, for this
    purpose, the generator should be subclassed and the __convert method
    should be overridden.
    """

    def __init__(
        self, release: NovaRelease, gi: GitIntegration, config=None
    ) -> None:
        if config is None:
            config = Config()

        self.__release = release
        self.__gi = gi

        output_path = config.get_notes_folder_path(
            self.__release.version, self.__release.delivery, ""
        )
        self.__output_path = fs.sanitize_filename(output_path)

    def __ensure_output_folder_exists(self) -> None:
        """
        Ensures the output folder exists or creates it if not.
        """
        if not os.path.exists(self.__output_path):
            os.makedirs(self.__output_path)

    def __generate_single_component_notes(
        self, component: NovaComponent
    ) -> Optional[str]:
        """
        Generates release notes for a single component.

        :param component: component to generate release notes for
        :return: path to the release notes file
        """
        assert component.repo is not None

        sources_dir = self.__gi.clone(component.repo.url)
        annotation = self.__release.title
        annotated_tags = self.__gi.list_tags_with_annotation(
            sources_dir, annotation
        )
        if not annotated_tags:
            return None
        tag_name = annotated_tags[0]
        self.__gi.checkout(sources_dir, tag_name)
        changelog_path = fs.search_changelog(sources_dir)
        if not changelog_path:
            return None
        filename = fs.gen_release_notes_filename(component.name, tag_name)
        filepath = f"{self.__output_path}/{filename}"
        return self.__convert(changelog_path, filepath)

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
        for a given release.

        :return: True if the generator can generate release
        notes for a given release
        """
        return self.__release.get_status() == Status.DONE

    def generate(self) -> dict[str, str]:
        """
        Generates release notes for a given release.

        :return: dictionary with component name as a key and
        absolute path to the release notes file as a value
        """
        self.__ensure_output_folder_exists()

        result = {}
        for component in self.__release:
            if component.status != Status.DONE:
                result[component.name] = None
                continue
            filepath = self.__generate_single_component_notes(component)
            result[component.name] = (
                os.path.abspath(filepath) if filepath else None
            )

        return result
