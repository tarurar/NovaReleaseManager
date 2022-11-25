"""
Nova task component module
"""
from core.nova_status import Status


class NovaTask:
    """Nova task"""

    @classmethod
    def map_jira_issue_status(cls, status):
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

    def __init__(self, name: str, status: Status, summary: str = ''):
        if not name:
            raise ValueError('Task name is not defined')
        if status is None:
            raise ValueError('Task status is not defined')

        self._name = name
        self._status = status
        self._summary = summary

    @property
    def status(self):
        """Task status"""
        return self._status

    @property
    def name(self):
        """Task name"""
        return self._name

    @property
    def summary(self):
        """Task summary"""
        return self._summary

    def get_release_notes(self) -> str:
        """Returns release notes for task"""
        key = self._name.strip().upper()
        summary = self._summary.split(
            ']')[-1].strip().lstrip('[').rstrip('.').strip().capitalize()
        ending = '' if summary.endswith('.') else '.'

        return f'{key}: {summary}{ending}'
