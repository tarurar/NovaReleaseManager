"""
Text helper functions
"""

from typing import Optional


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
    if 'delivery' in normalized_line and normalized_line.startswith('##'):
        words = normalized_line.split()
        potential_version = words[1]
        version = None
        if potential_version.replace('.', '').isdigit():
            version = potential_version
        return version
    return None
