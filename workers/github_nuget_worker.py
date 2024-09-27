"""
Release workflow for GitHub repositories
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
from integration.gh import GitHubIntegration
from integration.git import GitIntegration
from workers.release_worker import ReleaseWorker


class GitHubNugetPackageReleaseWorker(ReleaseWorker):
    """
    Nuget package release worker for GitHub hosted repositories.
    Doesn't create any releases effectively since the
    workflow is not yet implemented.
    Prints information about the latest release,
    latest tag and latest release notes.
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
        self._gh = gh
        self._gi = gi

    def release_component(
        self, component: NovaComponent
    ) -> Optional[NovaComponentRelease]:
        """
        GitHub nuget release workflow implementation

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

            repo = self._gh.get_repository(component.repo.url)
            latest_release = repo.get_latest_release()
            if latest_release is None:
                raise FileNotFoundError("Latest release not found")
            print("Latest release notes from GitHub:")
            print(latest_release.title)
            print(latest_release.html_url)
            print(latest_release.author.name)
            print(latest_release.created_at)
            print(latest_release.tag_name)
            print("Notes:")
            print(latest_release.body)
            print("===")

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
                latest_release.tag_name, latest_release.html_url
            )
        finally:
            fs.remove_dir(sources_dir)
