"""
Jira query language request builder tests
"""

from jira_utils import build_jql


def test_when_optional_params_are_empty():
    jql = build_jql('project')
    assert 'project=' in jql


def test_when_fix_version_is_provided():
    jql = build_jql('project', fix_version='fix_version')
    assert 'fixVersion=' in jql


def test_when_component_is_provided():
    jql = build_jql('project', component='component')
    assert 'component=' in jql


def test_when_all_params_are_provided():
    jql = build_jql('project', fix_version='fix_version',
                    component='component')
    assert 'fixVersion=' in jql
    assert 'component=' in jql
