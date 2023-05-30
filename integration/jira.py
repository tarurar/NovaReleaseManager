"""
Jira integration layer module.
"""

from jira import JIRA, JIRAError
from jira.resources import Issue, Component
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
