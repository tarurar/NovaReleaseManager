"""
Release workflow for GitHub hosted components
"""

from subprocess import call
from typing import Optional

from packaging.version import Version

import changelog
import fs_utils as fs
import msbuild
import text_utils as txt
from config import Config
from core.cvs import GitCloudService
from core.nova_component import NovaComponent
from core.nova_component_release import NovaComponentRelease
from core.nova_release import NovaRelease
from integration.gh import GitHubIntegration
from integration.git import GitIntegration
from ui import console
from workers.release_worker import ReleaseWorker


class GitHubReleaseWorker(ReleaseWorker):
    """
    GitHub release worker
    """

    @property
    def git_cloud(self) -> GitCloudService:
        return GitCloudService.GITHUB

    def __init__(
        self,
        release: NovaRelease,
        gh: GitHubIntegration,
        gi: GitIntegration,
        config=None,
    ) -> None:
        if config is None:
            config = Config()
        super().__init__(release, config)
        self.__gh = gh
        self.__gi = gi

    # pylint: disable=too-many-statements
    def release_component(
        self, component: NovaComponent
    ) -> Optional[NovaComponentRelease]:
        """
        Creates a tag in the repository and publishes github release
        """
        super().release_component(component)

        assert (
            component.repo is not None
        )  # assure Pylance that component.repo is not None

        # CHANGELOG.md update
        sources_dir = self.__gi.clone(component.repo.url)
        try:
            changelog_path = fs.search_changelog(sources_dir)
            if changelog_path is None:
                raise FileNotFoundError("Change log file not found")
            parsed_version = changelog.parse_version(changelog_path)
            new_version = txt.next_version(parsed_version)
            latest_tag = self.__gi.get_latest_tag(sources_dir)
            print(f"Current version from changelog: {str(parsed_version)}")
            print(f"Latest known tag from repository: {latest_tag}")
            print(f"New suggested version: {str(new_version)}")
            print("Please enter new version or quit to accept suggestion")
            entered_version = console.input_value("new version")
            # since the new tag will be created using this version,
            # it should be validated first
            if entered_version is not None:
                new_version = Version(entered_version)

            release_notes_title = txt.build_release_title_md(
                self._release.title, str(new_version)
            )
            # revisions are unknown at this point and actually are not required
            # since notes are being generated for changelog only.
            # revisions are required to build diff url for github release only
            component_notes = component.get_release_notes(None, None)
            release_notes = release_notes_title + "\n" + component_notes
            changelog.insert_release_notes(changelog_path, release_notes)

            # open external editor to edit release notes
            call([self._text_editor, changelog_path])
            input(
                "Press Enter to continue when you are done"
                + " with editing file in external editor ..."
            )
            msbuild.update_solution_version(sources_dir, new_version)

            tag_name = f"v{str(new_version)}"
            self.__gi.commit(sources_dir, f"Version {str(new_version)}")
            self.__gi.tag(sources_dir, tag_name, self._release.title)

        finally:
            fs.remove_dir(sources_dir)

        # get a tag for previous git release to build diff url
        previous_tag = self.__gh.select_or_autodetect_tag(
            component.repo.url, exclude=list(tag_name)
        )
        if previous_tag is None:
            return None

        # create github release
        repo = self.__gh.get_repository(component.repo.url)
        github_release_notes = component.get_release_notes(
            previous_tag.name, tag_name
        )
        github_release = repo.create_git_release(
            tag_name, self._release.title, github_release_notes
        )
        if github_release is None:
            raise IOError(f"Could not create release for tag {tag_name}")

        return NovaComponentRelease(
            github_release.tag_name, github_release.html_url
        )
