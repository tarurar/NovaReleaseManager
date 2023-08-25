"""
The release manager is responsible for managing the release process.
"""

import logging
from subprocess import call

import fs_utils as fs
from core.cvs import GitCloudService
from core.nova_component import NovaComponent
from core.nova_release import NovaRelease
from core.nova_status import Status
from integration.git import GitIntegration
from integration.gh import GitHubIntegration
from integration.jira import JiraIntegration
import bitbucket_release_flow as bbrf


class ReleaseManager:
    """The release manager is responsible for managing the release process."""

    # todo: add dependent client packages update validation.
    # Common issue: package updated but not mentioned in release notes

    default_text_editor = "vim"

    def __init__(
        self,
        jira: JiraIntegration,
        github_client: GitHubIntegration,
        git_client: GitIntegration,
        text_editor: str,
    ) -> None:
        self.__ji = jira
        self.__text_editor = (
            text_editor
            if text_editor is not None
            else ReleaseManager.default_text_editor
        )
        self.__gh = github_client
        self.__g = git_client

    def release_component(
        self, release: NovaRelease, component: NovaComponent
    ) -> tuple[str, str]:
        """
        Creates a tag in the repository and publishes a release,
        interacts with user to get the tag name.

        :param release: release model
        :param component: component to release
        :param branch: branch the tag will be created on
        :return: tag name and release url as a tuple
        """
        if component is None:
            raise ValueError("Component is not specified")

        if component.status == Status.DONE:
            raise ValueError(
                f"Component [{component.name}] is already released"
            )

        if component.status != Status.READY_FOR_RELEASE:
            raise ValueError(
                f"Component [{component.name}] is not ready for release"
            )

        if component.repo is None:
            raise ValueError(
                f"Component [{component.name}] does not have repository"
            )

        git_release = None
        if component.repo.git_cloud == GitCloudService.BITBUCKET:
            # todo: git cli has to be installed and configured
            # to access bitbucket and to push into master
            self.release_component_bitbucket(release, component)
        elif component.repo.git_cloud == GitCloudService.GITHUB:
            git_release = self.__gh.create_git_release(release, component)
            if git_release is None:
                return "", ""

        # moving jira issues to DONE
        for task in component.tasks:
            error_text = self.__ji.transition_issue(
                task.name, "Done", f"{release.title} released"
            )
            if error_text:
                logging.warning(
                    "Could not transition issue %s due to error: %s",
                    task.name,
                    error_text,
                )

        if component.repo.git_cloud == GitCloudService.BITBUCKET:
            return "Bitbucket tag to be", "Bitbucket tag url to be"
        elif component.repo.git_cloud == GitCloudService.GITHUB:
            if git_release is None:
                raise IOError("Could not create release")
            return git_release.tag_name, git_release.html_url
        else:
            raise ValueError(
                f"Unknown git cloud service {component.repo.git_cloud}"
            )

    def release_component_bitbucket(
        self,
        release: NovaRelease,
        component: NovaComponent,
        is_hotix: bool = False,
    ):
        if component.repo is None:
            raise ValueError("Component does not have repository")

        print(f"Cloning repository from url [{component.repo.url}]...")
        sources_dir = self.__g.clone(component.repo.url)
        print(f"Cloned repository into [{sources_dir}]")
        try:
            changelog_path = fs.search_changelog(sources_dir)
            if changelog_path is None:
                raise FileNotFoundError("Change log file not found")
            parsed_version = bbrf.parse_version_from_changelog(changelog_path)
            new_version = bbrf.increase_version(parsed_version, is_hotix)

            # todo: add deployment section if there is any jira task with
            # deployment comment
            release_notes_title = bbrf.build_release_title_md(
                release, new_version
            )
            component_notes = component.get_release_notes(None, None)
            release_notes = release_notes_title + "\n" + component_notes
            bbrf.insert_release_notes(changelog_path, release_notes)

            # open external editor to edit release notes
            call([self.__text_editor, changelog_path])
            input(
                "Press Enter to continue when you are done"
                + " with editing file in external editor ..."
            )
            bbrf.update_solution_version(sources_dir, new_version)

            # commit changes
            # todo: add only csproj and changelog files
            self.__g.commit(sources_dir, f"Version {str(new_version)}")
            tag_name = f"nova-{str(new_version)}"
            self.__g.tag(sources_dir, tag_name, f"Version {tag_name} release")

        finally:
            fs.remove_dir(sources_dir)
