"""
Release repository module
"""

from functools import partial
from jira import Issue
from core.nova_component import NovaComponent, NovaEmptyComponent
from core.nova_component_type import NovaComponentType
from core.nova_release import NovaRelease
import jira_utils as ju
from integration.jira import JiraIntegration


class NovaReleaseRepository:
    """
    Loads a release domain object from Jira
    """

    def __init__(self, jira: JiraIntegration) -> None:
        self.__ji = jira

    def get_packages(self, project_code: str) -> list[NovaComponent]:
        """
        Loads a list of packages for a project

        :param project_code: project code
        :return: list of packages
        """
        packages = [
            pkg
            for cmp in self.__ji.get_components(project_code)
            if (pkg := ju.parse_jira_component(cmp))
            and pkg.ctype
            in (NovaComponentType.PACKAGE, NovaComponentType.PACKAGE_LIBRARY)
            and not isinstance(pkg, NovaEmptyComponent)
        ]

        return packages

    def get_services(self, project_code: str) -> list[NovaComponent]:
        """
        Loads a list of services for a project

        :param project_code: project code
        :return: list of services
        """
        services = [
            svc
            for cmp in self.__ji.get_components(project_code)
            if (svc := ju.parse_jira_component(cmp))
            and svc.ctype == NovaComponentType.SERVICE
            and not isinstance(svc, NovaEmptyComponent)
        ]

        return services

    def get(
        self, project_code: str, version: str, delivery: str
    ) -> NovaRelease:
        """
        Loads a release model by project code, version and delivery

        :param project_code: project code
        :param version: version to release
        :param delivery: delivery number
        :return: release model
        """
        release = NovaRelease(project_code, version, delivery)

        components = [
            ju.parse_jira_component(cmp)
            for cmp in self.__ji.get_components(project_code)
        ]

        release_jira_issues = self.__ji.get_issues(project_code, str(release))

        for component in components:
            if isinstance(component, NovaEmptyComponent):
                continue

            filter_func = partial(
                ju.filter_jira_issue, component_name=component.name
            )
            component_jira_issues: list[Issue] = list(
                filter(
                    filter_func,
                    release_jira_issues,
                )
            )
            component_tasks = [
                ju.parse_jira_issue(issue) for issue in component_jira_issues
            ]
            if len(component_tasks) > 0:
                component.add_tasks(component_tasks)
                release.add_component(component)

        return release

    def set_released(self, rel: NovaRelease) -> bool:
        """
        Update JIRA's release status to RELEASED
        """
        # check internal state of the domain object
        if not rel.can_release_version():
            return False

        # check external state of JIRA release
        if not self.__ji.can_release_version(rel.project, rel.title):
            return False

        # update JIRA release state
        self.__ji.mark_version_as_released(rel.project, rel.title)
        return True
