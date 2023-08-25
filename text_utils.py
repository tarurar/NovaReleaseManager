"""
Text helper functions
"""

from typing import Optional
from packaging.version import Version


def try_extract_nova_component_version(line: str) -> Optional[str]:
    """
    Extracts version information from line of text.
    Expected line format is:
    '## <Version> [Nova 2] Delivery <Delivery number> (<Date>)'.
    Examples:
        '## 1.0.0 Nova 2 Delivery 1 (January 1, 2019)'
        '## 1.0.0 Delivery 1 (January 1, 2019)'
        '## 1.0.0 Delivery 1'
    :param line: line of text
    :return: version string or None
    """
    normalized_line = line.lower()
    if "delivery" in normalized_line and normalized_line.startswith("##"):
        words = normalized_line.split()
        potential_version = words[1]
        version = None
        if potential_version.replace(".", "").isdigit():
            version = potential_version
        return version
    return None


def next_version(version: Version, is_hotfix: bool = False) -> Version:
    """
    Calculates the next version based on the current version.

    :param version: base version
    :param is_hotfix: is hotfix
    :return: calculated version
    """
    major = version.major
    minor = version.minor if is_hotfix else version.minor + 1
    micro = version.micro + 1 if is_hotfix else 0

    return Version(f"{major}.{minor}.{micro}")
