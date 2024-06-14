"""
Zipper module
"""

import zipfile
from typing import Optional
from os.path import basename

from config import Config


class Zipper:
    """
    Zipper is a simple utility to zip and unzip files.
    """

    def __init__(
        self,
        nova_version: str,
        delivery: str,
        hotfix: Optional[str] = None,
        config=None,
    ):
        if config is None:
            config = Config()

        self._nova_version = nova_version
        self._delivery = delivery
        self._hotfix = hotfix
        self._output_path = config.get_artifacts_folder_path(
            self._nova_version, self._delivery, self._hotfix
        )

    def zip_notes(self, notes: dict[str, str]):
        """
        Zips the release notes.

        :param notes: dictionary with component name as a key and
        absolute path to the release notes file as a value
        :return: path to the zipped release notes file
        """
        output_file_path = self._build_notes_file_path()
        with zipfile.ZipFile(
            output_file_path, "w", zipfile.ZIP_DEFLATED
        ) as zipf:
            for _, path in notes.items():
                zipf.write(path, basename(path))

        return output_file_path

    def _build_notes_file_path(self) -> str:
        """
        Builds the name of the release notes file.

        :return: name of the release notes file
        """
        file_name = (
            f"nova{self._nova_version}_delivery{self._delivery}"
            + (f"_hotfix{self._hotfix}" if self._hotfix else "")
            + "_release_notes.zip"
        )

        return f"{self._output_path}/{file_name}"
