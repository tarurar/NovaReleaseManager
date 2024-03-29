"""
Nova task component module
"""
from typing import Optional
from core.nova_status import Status


class NovaTask:
    """Nova task"""

    deployment_asterisk = "*"

    @classmethod
    def map_jira_issue_status(cls, status):
        """Maps Jira issue status to Nova task status"""
        match status:
            case "Selected For Release":
                result = Status.READY_FOR_RELEASE
            case "Done":
                result = Status.DONE
            case "In Development":
                result = Status.IN_DEVELOPMENT
            case "Ready for UAT":
                result = Status.IN_DEVELOPMENT
            case "Ready for testing":
                result = Status.IN_DEVELOPMENT
            case "In Testing":
                result = Status.IN_DEVELOPMENT
            case "Ready for Review":
                result = Status.IN_DEVELOPMENT
            case "Open":
                result = Status.IN_DEVELOPMENT
            case _:
                result = Status.UNDEFINED

        return result

    def __init__(
        self,
        name: str,
        status: Status,
        summary: str = "",
        deployment: Optional[str] = None,
    ):
        if not name:
            raise ValueError("Task name is not defined")

        self.__name = name
        self.__status = status
        self.__summary = summary
        self.__deployment = deployment

    @property
    def status(self):
        """Task status"""
        return self.__status

    @property
    def name(self):
        """Task name"""
        return self.__name

    @property
    def summary(self):
        """Task summary"""
        return self.__summary

    @property
    def deployment(self):
        """Task deployment instructions"""
        return self.__deployment

    def get_release_notes(self, preview=False) -> str:
        """
        Returns release notes for task

        :param preview: if True, returns preview release notes which
            includes asterisk if task has deployment instructions
        :return: release notes
        """
        key = self.__name.strip().upper()
        summary = (
            self.__summary.split("]")[-1]
            .strip()
            .lstrip("[")
            .rstrip(".")
            .strip()
            .capitalize()
        )
        ending = "" if summary.endswith(".") else "."
        asterisk_or_not = (
            (NovaTask.deployment_asterisk if self.__deployment else "")
            if preview
            else ""
        )

        return f"{key}{asterisk_or_not}: {summary}{ending}"
