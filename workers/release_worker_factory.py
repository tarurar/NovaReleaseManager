"""
Release worker factory.
"""

from github import Github
from core.nova_component_type import NovaComponentType
from core.nova_release import NovaRelease
from integration.gh import GitHubIntegration
from integration.git import GitIntegration
from workers.bitbucket_nuget_worker import BitBucketNugetPackageReleaseWorker
from workers.github_nuget_worker import GitHubNugetPackageReleaseWorker
from workers.release_worker import ReleaseWorker
from workers.github_worker import GitHubReleaseWorker
from workers.bitbucket_worker import BitbucketReleaseWorker
from config import Config


class ReleaseWorkerFactory:  # pylint: disable=too-few-public-methods
    """
    Release worker factory.
    """

    @staticmethod
    def create_worker(
        worker_type: str,
        component_type: NovaComponentType,
        release: NovaRelease,
    ) -> ReleaseWorker:
        """
        Creates a release worker of the specified type.
        """
        config = Config()

        if component_type in [
            NovaComponentType.PACKAGE,
            NovaComponentType.PACKAGE_LIBRARY,
        ]:
            if worker_type == "github":
                gh_client = Github(config.data["github"]["accessToken"])

                return GitHubNugetPackageReleaseWorker(
                    release,
                    GitHubIntegration(gh_client),
                    GitIntegration(),
                    config,
                )

            if worker_type == "bitbucket":
                return BitBucketNugetPackageReleaseWorker(
                    release, GitIntegration(), config
                )

        if worker_type == "bitbucket":
            return BitbucketReleaseWorker(release, GitIntegration(), config)

        if worker_type == "github":
            gh_client = Github(config.data["github"]["accessToken"])

            return GitHubReleaseWorker(
                release, GitHubIntegration(gh_client), GitIntegration(), config
            )

        raise ValueError(f"Unknown release worker type: {worker_type}")
