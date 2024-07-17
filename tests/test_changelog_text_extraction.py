"""
Unit tests for the function extract_latest_release_notes 
from text_utils.py
"""

import os
import pytest
from text_utils import extract_latest_release_notes


def read_test_case(filename):
    with open(filename, "r", encoding="utf-8") as file:
        content = file.read()
        changelog, expected_output = content.split("===", 1)
        return changelog.strip(), expected_output.strip()


test_files = [
    "test_case1.txt",
    "test_case2.txt",
    "test_case3.txt",
    "test_case4.txt",
    "test_case5.txt",
    "test_case6.txt",
]


@pytest.mark.parametrize("test_file", test_files)
def test_extract_latest_release_notes(test_file):
    file_path = os.path.join(
        os.path.dirname(__file__), "changelog_data", test_file
    )
    changelog, expected_output = read_test_case(file_path)
    assert extract_latest_release_notes(changelog) == expected_output
