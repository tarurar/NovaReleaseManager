"""
Release workflow for GitHub hosted components
"""

from typing import Optional
from core.nova_component_release import NovaComponentRelease
from core.cvs import GitCloudService
from core.nova_component import NovaComponent
from core.nova_release import NovaRelease
from integration.gh import GitHubIntegration
from workers.release_worker import ReleaseWorker


class GitHubReleaseWorker(ReleaseWorker):
    """
    GitHub release worker
    """

    @property
    def git_cloud(self) -> GitCloudService:
        return GitCloudService.GITHUB

    def __init__(self, release: NovaRelease, gh: GitHubIntegration) -> None:
        super().__init__(release)
        self.__gh = gh

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

        # get a tag for the git release
        tag = self.__gh.select_or_create_tag(
            component.repo.url, self._release.title
        )
        if tag is None:
            return None

        # get a tag for previous git release
        previous_tag = self.__gh.select_or_autodetect_tag(
            component.repo.url, exclude=list(tag.name)
        )
        if previous_tag is None:
            return None

        # create github release
        repo = self.__gh.get_repository(component.repo.url)
        github_release_notes = component.get_release_notes(
            previous_tag.name, tag.name
        )
        github_release = repo.create_git_release(
            tag.name, self._release.title, github_release_notes
        )
        if github_release is None:
            raise IOError(f"Could not create release for tag {tag.name}")

        return NovaComponentRelease(
            github_release.tag_name, github_release.html_url
        )
