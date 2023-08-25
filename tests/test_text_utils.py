"""
Text helper functions tests
"""

import pytest
from packaging.version import Version
import text_utils as txt


@pytest.mark.parametrize(
    "line, expected_version",
    [
        ("## 1.0.0 nova 2 delivery version", "1.0.0"),
        ("## 1.0 nova 2 delivery version", "1.0"),
        ("## 1 nova 2 delivery version", "1"),
        ("1.0.0 nova 2 delivery ", None),
        ("## 1.0.0 delivery", "1.0.0"),
        ("## nova 2 delivery", None),
        ("## 2.0.0 NOVA 2 DELIVERY", "2.0.0"),
        ("## 3.0.0 NoVa 2 DeLiVeRy", "3.0.0"),
        ("1.0.0", None),
    ],
)
def test_try_extract_nova_component_version(line, expected_version):
    version = txt.try_extract_nova_component_version(line)
    assert version == expected_version


@pytest.mark.parametrize(
    "version, is_hotfix, expected_version",
    [
        ("1.0.0", False, "1.1.0"),
        ("1.0.0", True, "1.0.1"),
        ("1.1.1", False, "1.2.0"),
        ("1.1.1", True, "1.1.2"),
    ],
)
def test_next_version(version, is_hotfix, expected_version):
    version_object = Version(version)
    expected_version_object = Version(expected_version)
    next_version_object = txt.next_version(version_object, is_hotfix)
    assert next_version_object == expected_version_object


@pytest.mark.parametrize(
    "release_title",
    ["", " "],
)
def test_build_release_title_md_raises_error_when_title_is_not_specified(
    release_title,
):
    with pytest.raises(ValueError):
        txt.build_release_title_md(release_title, "1.0.0")


@pytest.mark.parametrize("version", ["", " "])
def test_build_release_title_md_raises_error_when_version_is_not_specified(
    version,
):
    with pytest.raises(ValueError):
        txt.build_release_title_md("Release title", version)


def test_build_release_title_md_includes_version():
    release_title = "Release title"
    version = "1.0.0"
    actual_title = txt.build_release_title_md(release_title, version)
    assert version in actual_title


def test_build_release_title_md_includes_release_title():
    release_title = "Release title"
    version = "1.0.0"
    actual_title = txt.build_release_title_md(release_title, version)
    assert release_title in actual_title
