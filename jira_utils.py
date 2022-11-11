"""
Jira utility helper function module.
"""

from typing import Optional
from urllib.parse import urlparse

import validators
from jira.resources import Issue

from core.cvs import CodeRepository, GitCloudService
from core.nova_component import NovaComponent, NovaEmptyComponent
from core.nova_status import Status
from core.nova_task import NovaTask


def parse_jira_cmp_descr(descr: str) -> tuple[
        Optional[GitCloudService],
        Optional[str]]:
    """
    Parse Jira component description and return cloud service and
    repository URL. It is epected that JIRA component description
    will be in the following format:
        Bitbucket: http(s)://bitbucket.org/<repo>
        GitHub: http(s)://github.com/<company>/<repo> or
            just <company>/<repo>
    """
    if descr is None:
        return None, None

    normalized_description = descr.strip().lower()

    if not normalized_description.startswith('http'):
        normalized_description = 'http://' + normalized_description

    if validators.url(normalized_description):
        url_parse_result = urlparse(normalized_description)
        if 'github' in url_parse_result.hostname:
            return GitCloudService.GITHUB, descr
        if 'bitbucket' in url_parse_result.hostname:
            return GitCloudService.BITBUCKET, descr
    return None, None


def build_jql(project: str, fix_version='', component='') -> str:
    """
    Build JQL query string.
    """
    jql = f'project={project}'
    if fix_version:
        jql += f' AND fixVersion="{fix_version}"'
    if component:
        jql += f' AND component="{component}"'
    return jql


def parse_jira_issue(issue: Issue) -> NovaTask:
    """
    Parse Jira issue.
    """
    if issue is None:
        raise ValueError('Issue is None')
    if not hasattr(issue, 'key'):
        raise ValueError('Issue has no key')
    if not issue.key:
        raise ValueError('Issue key is empty')
    if len(issue.fields.components) == 0:
        raise ValueError(f'Issue [{issue.key}] has no component')
    if len(issue.fields.components) > 1:
        raise ValueError(
            f'Issue [{issue.key}] has more than one component')

    status = NovaTask.map_jira_issue_status(issue.fields.status.name)
    if status == Status.UNDEFINED:
        raise ValueError(
            f'[{issue.key}] has invalid status [{issue.fields.status.name}]')

    return NovaTask(issue.key, status, issue.fields.summary)


def parse_jira_component(cmp: object) -> NovaComponent:
    """
    Parse Jira component.
    """
    if cmp is None:
        raise ValueError('Component is None')
    if not hasattr(cmp, 'name'):
        raise ValueError('Component has no name')
    if cmp.name is None:
        raise ValueError('Component name is empty')
    if cmp.name.strip().lower() == NovaEmptyComponent.default_component_name:
        return NovaEmptyComponent()
    if not hasattr(cmp, 'description'):
        raise ValueError(f'Component [{cmp.name}] has no description')
    if cmp.description is None or cmp.description.strip() == '':
        raise ValueError(f'Component [{cmp.name}] has empty description')

    cloud_service, repo_url = parse_jira_cmp_descr(cmp.description)
    if cloud_service is None or repo_url is None:
        raise ValueError(f'Component [{cmp.name}] has invalid description, '
                         f'expected to be in the following format: '
                         f'Bitbucket: http(s)://bitbucket.org/<repo> or '
                         f'GitHub: http(s)://github.com/<company>/<repo> or '
                         f'just <company>/<repo>')

    return NovaComponent(
        cmp.name,
        CodeRepository(cloud_service, repo_url))


def filter_jira_issue(jira_issue, cmp_name) -> bool:
    """
    Filter Jira issue by component name.
    """
    jira_name = jira_issue.fields.components[0].name.strip().lower()
    nova_name = cmp_name.strip().lower()

    return jira_name == nova_name
