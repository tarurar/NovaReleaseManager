"""
Nova component release
"""

from dataclasses import dataclass


@dataclass
class NovaComponentRelease:
    """
    Nova component release
    """

    tag_name: str
    url: str
