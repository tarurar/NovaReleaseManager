"""
Nova task component module
"""
from core.nova_status import Status


class NovaTask:
    """Nova task"""

    @staticmethod
    def map_jira_issue_status(status):
        """Maps Jira issue status to Nova task status"""
        match status:
            case 'Selected For Release':
                return Status.READY_FOR_RELEASE
            case 'Done':
                return Status.DONE
            case 'In Development':
                return Status.IN_DEVELOPMENT
            case 'Ready for UAT':
                return Status.IN_DEVELOPMENT
            case 'In Testing':
                return Status.IN_DEVELOPMENT
            case 'Ready for Review':
                return Status.IN_DEVELOPMENT
            case _:
                return Status.UNDEFINED

    def __init__(self, name, status):
        self._name = name
        self._status = status

    @property
    def status(self):
        """Task status"""
        return self._status

    @property
    def name(self):
        """Task name"""
        return self._name
