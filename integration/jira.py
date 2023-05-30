"""
Jira integration layer module.
"""

from typing import Optional

from jira import JIRA, JIRAError
from jira.resources import Component, Issue, Version

import jira_utils as ju


class JiraIntegration:
    """Jira integration service

    Connects to Jira using basic authentication.
    """

    def __init__(self, host, username, password) -> None:
        self.__j = JIRA(host, basic_auth=(username, password))

    def get_issues(
            self,
            project_code: str,
            delivery: str,
            component_name: str = '') -> list[Issue]:
        """
        Get JIRA issues for a component in a particular delivery

        :param project_code: project code
        :param delivery: delivery number
        :param component_name: component name
        :return: list of JIRA issues
        """

        result = []
        i = 0
        chunk_size = 50

        jql = ju.build_jql(project_code, delivery, component_name)
        while True:
            try:
                issues = self.__j.search_issues(
                    jql, maxResults=chunk_size, startAt=i)
            except JIRAError:
                return []
            i += chunk_size
            result += issues.iterable
            if i >= issues.total:
                break
        return result

    def get_components(self, project_code: str) -> list[Component]:
        """
        Get all components for a project

        :param project_code: project code
        :return: list of components
        """
        return self.__j.project_components(project_code)

    # todo: probably can be removed
    def get_version_by_name(
            self, project_code: str, version_name: str) -> Optional[Version]:
        """
        Get project version by name

        :param project_code: project code
        :param version_name: version name
        :return: project version or None
        """
        return self.__j.get_project_version_by_name(
            project=project_code, version_name=version_name)

    def mark_version_as_released(
            self, project_code: str, version_name: str) -> None:
        """
        Mark project version as released

        :param project_code: project code
        :param version_name: version name
        """
        version = self.__j.get_project_version_by_name(
            project=project_code, version_name=version_name)
        if version is None:
            raise ValueError(f'Version {version_name} not found')
        version.update(released=True)

    @classmethod
    def can_release_version(cls, version: Optional[Version]) -> bool:
        """
        Check if a version can be released

        :param version: project version
        :return: True if version can be released, False otherwise
        """
        if version is None:
            return False
        if version.archived:
            return False
        if version.released:
            return False
        return True
