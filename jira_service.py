"""
JIRA API client wrapper module
"""
from datetime import datetime
from jira import JIRA
from core.cvs import CodeRepository, GitCloudService


def build_release_comment():
    """"Generates release comment"""
    return f"Released on {datetime.utcnow().strftime('%Y-%m-%d %H:%M:%S')} UTC"


def try_get_component_repository(component):
    """Returns component repository"""
    if component is None:
        return None
    if component.description is None:
        return None
    cvs_type = component.description.split(':')[0]
    url = component.description.split(':')[1]
    if cvs_type.lower() == 'github':
        return CodeRepository(GitCloudService.GITHUB, url)
    if cvs_type.lower() == 'bitbucket':
        return CodeRepository(GitCloudService.BITBUCKET, url)
    return None


class JiraService:
    """JIRA API client wrapper"""
    ready_for_release_status = 'Selected For Release'
    done_status = 'Done'

    @classmethod
    def get_issue_component(cls, issue):
        """Returns JIRA issue component name"""
        try:
            return issue.fields.components[0].name
        except IndexError:
            return None

    def __init__(self, url, username, password, project, release):
        self.project = project
        self.release = release
        self.jira = JIRA(url, basic_auth=(username, password))

    # def change_status_done(self, issues):
    #     comment = build_release_comment()
    #     for issue in issues:
    #         if issue.fields.status.name == self.ready_for_release_status:
    #             self.jira.transition_issue(
    #                issue, self.done_status, comment=comment)

    # def try_get_project(self):
    #     try:
    #         return self.jira.project(self.project)
    #     except JIRAError as e:
    #         if e.status_code == 404:
    #             return None
    #         else:
    #             raise e
    #
    # def try_get_component(self, component_name):
    #     try:
    #         components = self.jira.project_components(self.project)
    #     except JIRAError as e:
    #         if e.status_code == 404:
    #             return None
    #         else:
    #             raise e
    #
    #     return next((c for c in components if c.name == component_name), None)
