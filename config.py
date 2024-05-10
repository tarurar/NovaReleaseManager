"""
Configuration file for the application
"""

from dataclasses import dataclass
import json
from typing import Any, Optional
import fs_utils as fs


@dataclass
class PackageTagException:
    """
    Represents an exception for package tag
    """

    package: str
    tag_template: str


class Config:
    """
    Configuration for the application
    """

    DEFAULT_CONFIG_PATH = "config.json"

    data: dict[str, Any]
    _instance = None

    def __new__(cls, config_path: str = DEFAULT_CONFIG_PATH):
        # Singleton pattern
        if cls._instance is None:
            cls._instance = super(Config, cls).__new__(cls)
            if not config_path:
                config_path = cls.DEFAULT_CONFIG_PATH
            with open(config_path, encoding="utf-8") as file:
                cls._instance.data = json.load(file)
        return cls._instance

    def get_artifacts_folder_path(
        self, nova_version: str, delivery: str, hotfix: Optional[str] = None
    ):
        """
        Returns path to the folder where release artifacts should be stored.
        Path is sanitized which guarantees the folder can be created if required.

        :param nova_version: nova version
        :param delivery: delivery number
        :param hotfix: hotfix number
        :return: path to the folder where release artifacts should be stored
        """
        template = self.data["release"]["artifactsFolderPathTemplate"]
        if not template:
            raise ValueError(
                "artifactsFolderPathTemplate is not specified in config"
            )
        formatted = template.format(
            nova=f"Nova {nova_version}.",
            delivery=f"Delivery {delivery}.",
            hotfix=f" Hotfix {hotfix}" if hotfix else "",
        )

        return fs.sanitize_path(formatted)

    def get_package_tag_exceptions(self) -> list[PackageTagException]:
        """
        Reads a list of package tag exceptions from configuration file
        """
        try:
            tag_exceptions = self.data["release"]["packageTags"]["exceptions"]
            return list(
                map(
                    lambda e: PackageTagException(e["name"], e["tagTemplate"]),
                    tag_exceptions,
                )
            )
        except KeyError:
            return list[PackageTagException]()

    def get_package_tag_exception(
        self, package_name: str
    ) -> Optional[PackageTagException]:
        """
        Returns package tag exception for specified package name

        :param package_name: package name
        :return: package tag exception or None if not found
        """
        exceptions = self.get_package_tag_exceptions()
        for exception in exceptions:
            if exception.package == package_name:
                return exception
        return None
