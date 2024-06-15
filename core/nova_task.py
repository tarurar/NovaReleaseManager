"""
Nova task component module
"""

from dataclasses import dataclass
from typing import Optional
from core.nova_status import Status


@dataclass(frozen=True)
class NovaTask:
    """Nova task"""

    deployment_asterisk = "*"

    name: str
    status: Status
    summary: str = ""
    deployment: Optional[str] = None

    def __post_init__(self):
        if not self.name:
            raise ValueError("Task name is not defined")

    def get_release_notes(self, preview=False) -> str:
        """
        Returns release notes for task

        :param preview: if True, returns preview release notes which
            includes asterisk if task has deployment instructions
        :return: release notes
        """
        key = self.name.strip().upper()
        summary = (
            self.summary.rsplit("]", 1)[-1]
            .strip()
            .lstrip("[")
            .rstrip(".")
            .strip()
            .capitalize()
        )
        ending = "" if summary.endswith(".") else "."
        asterisk_or_not = (
            (NovaTask.deployment_asterisk if self.deployment else "")
            if preview
            else ""
        )

        return f"{key}{asterisk_or_not}: {summary}{ending}"

    @staticmethod
    def map_jira_issue_status(status):
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
