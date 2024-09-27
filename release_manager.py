"""
The release manager is responsible for managing the release process.
"""

import logging
from config import Config
from core.nova_component import NovaComponent
from core.nova_component_release import NovaComponentRelease
from core.nova_release import NovaRelease
from integration.jira import JiraIntegration
from workers.release_worker_factory import ReleaseWorkerFactory


class ReleaseManager:
    """The release manager is responsible for managing the release process."""

    def __init__(self) -> None:
        config = Config()

        self._ji = JiraIntegration(
            config.data["jira"]["host"],
            config.data["jira"]["username"],
            config.data["jira"]["password"],
        )

    def release_component(
        self, release: NovaRelease, component: NovaComponent
    ) -> NovaComponentRelease:
        """
        Creates a tag in the repository and publishes a release,
        interacts with user to get the tag name.

        :param release: release model
        :param component: component to release
        :return: component release
        """
        if component.repo is None:
            raise ValueError("Component repository is not specified")

        worker = ReleaseWorkerFactory.create_worker(
            component.repo.git_cloud.value, component.ctype, release
        )
        component_release = worker.release_component(component)

        if component_release is None:
            raise IOError(
                f"Could not create component release for {component.name}"
            )

        # moving jira issues to DONE
        for task in component.tasks:
            error_text = self._ji.transition_issue(
                task.name, "Done", f"{release.title} released"
            )
            if error_text:
                logging.warning(
                    "Could not transition issue %s due to error: %s",
                    task.name,
                    error_text,
                )

        return component_release
