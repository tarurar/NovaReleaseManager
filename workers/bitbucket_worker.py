"""
Release workflow for Bitbucket hosted components
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
from git_utils import get_git_tag_url
from integration.git import GitIntegration
from ui import console
from workers.release_worker import ReleaseWorker


class BitbucketReleaseWorker(ReleaseWorker):
    """
    Bitbucket release worker
    """

    @property
    def git_cloud(self) -> GitCloudService:
        return GitCloudService.BITBUCKET

    def __init__(
        self, release: NovaRelease, gi: GitIntegration, config=None
    ) -> None:
        if config is None:
            config = Config()
        super().__init__(release, config)
        self.__gi = gi

    # pylint: disable=too-many-statements
    def release_component(
        self, component: NovaComponent
    ) -> Optional[NovaComponentRelease]:
        """
        Bitbucket release workflow implementation

        :param component: component to release
        :return: release information
        """

        super().release_component(component)

        assert (
            component.repo is not None
        )  # assure Pylance that component.repo is not None

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
            self.__gi.commit_changelogs_and_csproj(
                sources_dir, f"Version {str(new_version)}"
            )
            self.__gi.tag(sources_dir, tag_name, self._release.title)

            return NovaComponentRelease(
                tag_name,
                get_git_tag_url(
                    GitCloudService.BITBUCKET,
                    component.repo.sanitized_url,
                    tag_name,
                ),
            )

        finally:
            fs.remove_dir(sources_dir)
