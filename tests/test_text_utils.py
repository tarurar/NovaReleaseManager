"""
Text helper functions tests
"""

import pytest
import text_utils as txt

@pytest.mark.parametrize('line, expected_version',[
    ('## 1.0.0 nova 2 delivery version', '1.0.0'),
    ('## 1.0 nova 2 delivery version', '1.0'),
    ('## 1 nova 2 delivery version', '1'),
    ('1.0.0 nova 2 delivery ', None),
    ('## 1.0.0 delivery', '1.0.0'),
    ('## nova 2 delivery', None),
    ('## 2.0.0 NOVA 2 DELIVERY', '2.0.0'),
    ('## 3.0.0 NoVa 2 DeLiVeRy', '3.0.0'),
    ('1.0.0', None)])
def test_try_extract_nova_component_version(line, expected_version):
    version = txt.try_extract_nova_component_version(line)
    assert version == expected_version
