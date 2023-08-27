"""
Configuration file for the application
"""

import json
from typing import Any


class Config:
    """
    Configuration for the application
    """

    data: dict[str, Any]
    _instance = None

    def __new__(cls):
        # Singleton pattern
        if cls._instance is None:
            cls._instance = super(Config, cls).__new__(cls)
            with open("config.json", encoding="utf-8") as file:
                cls._instance.data = json.load(file)
        return cls._instance
