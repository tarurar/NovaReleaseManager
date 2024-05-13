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

        self.__nova_version = nova_version
        self.__delivery = delivery
        self.__hotfix = hotfix
        self.__output_path = config.get_artifacts_folder_path(
            self.__nova_version, self.__delivery, self.__hotfix
        )

    def zip_notes(self, notes: dict[str, str]):
        """
        Zips the release notes.

        :param notes: dictionary with component name as a key and
        absolute path to the release notes file as a value
        :return: path to the zipped release notes file
        """
        output_file_path = self.__build_notes_file_path()
        with zipfile.ZipFile(
            output_file_path, "w", zipfile.ZIP_DEFLATED
        ) as zipf:
            for _, path in notes.items():
                zipf.write(path, basename(path))

        return output_file_path

    def __build_notes_file_path(self) -> str:
        """
        Builds the name of the release notes file.

        :return: name of the release notes file
        """
        file_name = (
            f"nova{self.__nova_version}_delivery{self.__delivery}"
            + (f"_hotfix{self.__hotfix}" if self.__hotfix else "")
            + "_release_notes.zip"
        )

        return f"{self.__output_path}/{file_name}"
