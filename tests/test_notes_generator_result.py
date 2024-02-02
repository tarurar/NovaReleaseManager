"""
Notes Generator Result Tests Module
"""

import pytest

from notes_generator import NotesGenerator


def test_when_both_path_and_error_are_none_then_raises_value_error():
    with pytest.raises(ValueError):
        NotesGenerator.Result()


def test_when_both_path_and_error_are_set_then_raises_value_error():
    with pytest.raises(ValueError):
        NotesGenerator.Result(path="path", error="error")
