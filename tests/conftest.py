"""
This module contains fixtures for the tests.
"""

import pytest
from tests.fakes import FakeConfig, FakeGitHub
from integration.github import GitHubIntegration

# region Fake input fixtures


@pytest.fixture(name="input_new_tag_values")
def fixture_input_new_tag_values():
    """
    The sequence of inputs emulates the following user actions:
    1. Empty input to skip tag selection from existing tags.
    2. Enter new name for the tag.
    """
    inputs = ["", "1.0.0"]
    return iter(inputs)


@pytest.fixture(name="input_new_tag")
def fixture_input_new_tag(input_new_tag_values):
    """
    This fixture returns a function which emulates user input.
    Separate fixture is needed to avoid reusing the same iterator
    for all tests.
    """

    def input_new_tag(_):
        return next(input_new_tag_values)

    return input_new_tag


@pytest.fixture(name="input_cancel_values")
def fixture_input_cancel_values():
    """
    The sequence of inputs emulates the following user actions:
    1. Empty input to skip tag selection from existing tags.
    2. Cancel tag creation by entering 'q'.
    """
    inputs = ["", "q"]
    return iter(inputs)


@pytest.fixture(name="input_cancel")
def fixture_input_cancel(input_cancel_values):
    def input_cancel(_):
        return next(input_cancel_values)

    return input_cancel


@pytest.fixture(name="input_second_tag_cancel_values")
def fixture_input_second_tag_cancel_values():
    """
    The sequence of inputs emulates the following user actions:
    1. Select the first tag from the list of existing tags.
    2. Cancel second tag selection by entering empty input.
    """
    inputs = ["1", ""]
    return iter(inputs)


@pytest.fixture(name="input_second_tag_cancel")
def fixture_input_second_tag_cancel(
    input_second_tag_cancel_values,
):
    def input_second_tag_cancel(_):
        return next(input_second_tag_cancel_values)

    return input_second_tag_cancel


@pytest.fixture(name="input_all_tag_values")
def fixture_input_all_tag_values():
    """
    The sequence of inputs emulates the following user actions:
    1. Select the first tag from the list of existing tags.
    2. Select the second tag from the list of existing tags.
    """
    inputs = ["1", "2"]
    return iter(inputs)


@pytest.fixture(name="input_all_tags")
def fixture_input_all_tags(input_all_tag_values):
    def input_all_tags(_):
        return next(input_all_tag_values)

    return input_all_tags


# endregion

# region Fake GitHub fixtures


@pytest.fixture(name="fake_config")
def fixture_fake_config(request):
    # use default FakeConfig if no param is provided
    return request.param if hasattr(request, "param") else FakeConfig()


@pytest.fixture(name="fake_github")
def fixture_fake_github(fake_config):
    return FakeGitHub(fake_config)


@pytest.fixture(name="integration")
def fixture_integration(fake_github):
    return GitHubIntegration(fake_github)


# endregion
