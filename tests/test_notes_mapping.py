"""
This module contains tests for the mappers module.
"""

import pytest
from notes_generator import NotesGenerator
from mappers import only_succeeded_notes


@pytest.fixture(name="sample_notes")
def fixture_sample_notes():
    return {
        "note1": NotesGenerator.Result(path="/path/to/note1.pdf"),
        "note2": NotesGenerator.Result(path="", error="Error"),
        "note3": NotesGenerator.Result(path="/path/to/note3.pdf"),
        "note4": NotesGenerator.Result(error="Error"),
        "note5": NotesGenerator.Result(path=" ", error="Error"),
        "note6": NotesGenerator.Result(path="/path/to/note6.pdf", error=""),
        "note7": NotesGenerator.Result(path="/path/to/note7.pdf", error=" "),
    }


def test_only_succeeded_notes(sample_notes):
    expected_result = {
        "note1": "/path/to/note1.pdf",
        "note3": "/path/to/note3.pdf",
        "note6": "/path/to/note6.pdf",
        "note7": "/path/to/note7.pdf",
    }
    assert only_succeeded_notes(sample_notes) == expected_result
