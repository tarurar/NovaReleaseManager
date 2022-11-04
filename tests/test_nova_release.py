"""
Nova release tests
"""

import pytest
from core.nova_status import Status as s
from core.nova_release import get_release_status


@pytest.mark.parametrize("component_statuses, expected_status", [
    ([s.UNDEFINED], s.UNDEFINED),
    ([s.UNDEFINED, s.IN_DEVELOPMENT], s.UNDEFINED),
    ([s.UNDEFINED, s.IN_DEVELOPMENT, s.READY_FOR_RELEASE], s.UNDEFINED),
    ([s.UNDEFINED, s.IN_DEVELOPMENT, s.READY_FOR_RELEASE, s.DONE], s.UNDEFINED),
    ([s.IN_DEVELOPMENT, s.READY_FOR_RELEASE, s.DONE], s.IN_DEVELOPMENT),
    ([s.READY_FOR_RELEASE, s.DONE], s.READY_FOR_RELEASE),
    ([s.DONE], s.DONE),
])
def test_release_status(component_statuses, expected_status):
    assert get_release_status(component_statuses) == expected_status
