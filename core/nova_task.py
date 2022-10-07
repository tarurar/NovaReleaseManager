"""Nova task component module"""
from .nova_status import Status


class NovaTask(object):
    """Nova task"""

    @staticmethod
    def map_jira_issue_status(status):
        """Maps Jira issue status to Nova task status"""
        match status:
            case 'Selected For Release':
                return Status.ReadyForRelease
            case 'Done':
                return Status.Done
            case 'In Development':
                return Status.InDevelopment
            case _:
                return Status.Undefined

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
