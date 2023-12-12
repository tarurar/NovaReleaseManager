"""
Configuration file for the application
"""

import json
from typing import Any, Optional


class Config:  # pylint: disable=too-few-public-methods
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

    def get_notes_folder_path(
        self, nova_version: str, delivery: str, hotfix: Optional[str] = None
    ):
        template = self.data["release"]["notesFolderPathTemplate"]
        if not template:
            raise ValueError(
                "notesFolderPathTemplate is not specified in config"
            )
        return template.format(
            nova=f"Nova {nova_version}.",
            delivery=f"Delivery {delivery}.",
            hotfix=f" Hotfix {hotfix}" if hotfix else "",
        )
