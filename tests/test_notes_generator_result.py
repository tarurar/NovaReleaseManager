"""
Notes Generator Result Tests Module
"""

import pytest

from notes_generator import NotesGenerator


def test_when_both_path_and_error_are_empty_then_raises_value_error():
    with pytest.raises(ValueError):
        NotesGenerator.Result("", "")


def test_when_both_path_and_error_are_set_then_raises_value_error():
    with pytest.raises(ValueError):
        NotesGenerator.Result(path="path", error="error")


@pytest.mark.parametrize(
    "path, error",
    [(1, 2), (1, ""), ("", 2), (" ", ""), ("", " ")],
)
def test_when_parameters_are_incorrect_then_raises_value_error(path, error):
    with pytest.raises(ValueError):
        NotesGenerator.Result(path, error)
