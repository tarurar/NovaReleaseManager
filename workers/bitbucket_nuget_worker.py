"""
Release workflow for Bitbucker repositories
which host Nuget packages
"""

from typing import Optional
import fs_utils as fs
import text_utils as txt
from config import Config
from core.cvs import GitCloudService
from core.nova_component import NovaComponent
from core.nova_component_release import NovaComponentRelease
from core.nova_release import NovaRelease
from git_utils import get_git_tag_url
from integration.git import GitIntegration
from workers.release_worker import ReleaseWorker


class BitBucketNugetPackageReleaseWorker(ReleaseWorker):
    """
    Nuget package release worker for BitBucket hosted repositories.
    Doesn't create any releases effectively since the
    workflow is not yet implemented.
    Prints information about the latest release,
    latest tag and latest release notes.
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
        self._gi = gi

    def release_component(
        self, component: NovaComponent
    ) -> Optional[NovaComponentRelease]:
        """
        Bitbucket nuget release workflow implementation

        :param component: component to release
        :return: release information
        """
        super().release_component(component)

        assert (
            component.repo is not None
        )  # assure Pylance that component.repo is not None

        sources_dir = self._gi.clone(component.repo.url)
        try:
            changelog_path = fs.search_changelog_first(sources_dir)
            if changelog_path is None:
                raise FileNotFoundError("Change log file not found")
            with open(changelog_path, "r", encoding="utf-8") as changelog_file:
                changelog_content = changelog_file.read()

            latest_notes = txt.extract_latest_release_notes(changelog_content)
            print("Latest release notes from CHANGELOG:")
            print(latest_notes)
            latest_tag = self._gi.get_latest_tag(sources_dir)
            print(f"Latest known tag from repository: {latest_tag}")

            release_done_decision = input(
                "Consider this information as completed release [Y/n/q]?"
            )
            if release_done_decision in ["n", "q"]:
                return None

            return NovaComponentRelease(
                latest_tag,
                get_git_tag_url(
                    GitCloudService.BITBUCKET,
                    component.repo.sanitized_url,
                    latest_tag,
                ),
            )
        finally:
            fs.remove_dir(sources_dir)
