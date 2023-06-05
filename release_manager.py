"""
The release manager is responsible for managing the release process.
"""

import logging
import re
from datetime import datetime
from subprocess import call
from tempfile import TemporaryDirectory

from git.repo import Repo
from github import Github
from packaging.version import InvalidVersion, Version, parse

import fs_utils as fs
from github_release_flow import GitHubReleaseFlow
from core.cvs import GitCloudService
from core.nova_component import NovaComponent
from core.nova_release import NovaRelease
from core.nova_status import Status
from integration.jira import JiraIntegration
import ui.console as console


class ReleaseManager:
    """The release manager is responsible for managing the release process."""
    # todo: add dependent client packages update validation.
    # Common issue: package updated but not mentioned in release notes

    default_text_editor = 'vim'

    def __init__(
            self,
            jira: JiraIntegration,
            github_client: Github,
            text_editor: str) -> None:
        self.__ji = jira
        self.__text_editor = text_editor if text_editor is not None else ReleaseManager.default_text_editor
        self.__github_flow = GitHubReleaseFlow(github_client)

    def release_component(
            self,
            release: NovaRelease,
            component: NovaComponent,
            branch: str = 'master') -> tuple[str, str]:
        """
        Creates a tag in the repository and publishes a release,
        interacts with user to get the tag name.

        :param release: release model
        :param component: component to release
        :param branch: branch the tag will be created on
        :return: tag name and release url as a tuple
        """
        if component is None:
            raise ValueError('Component is not specified')

        if component.status == Status.DONE:
            raise ValueError(
                f'Component [{component.name}] is already released')

        if component.status != Status.READY_FOR_RELEASE:
            raise ValueError(
                f'Component [{component.name}] is not ready for release')

        git_release = None
        if component.repo.git_cloud == GitCloudService.BITBUCKET:
            # TODO: git cli has to be installed and configured
            # to access bitbucket and to push into master
            self.release_component_bitbucket(release, component, branch)
        elif component.repo.git_cloud == GitCloudService.GITHUB:
            git_release = self.__github_flow.create_git_release(
                release, component)
            if git_release is None:
                return '', ''
        # moving jira issues to DONE
        for task in component.tasks:
            error_text = self.__ji.transition_issue(
                task.name, 'Done', f'{release.title} released')
            if error_text:
                logging.warning(
                    'Could not transition issue %s due to error: %s',
                    task.name,
                    error_text)

        if component.repo.git_cloud == GitCloudService.BITBUCKET:
            return 'Bitbucket tag to be', 'Bitbucket tag url to be'
        elif component.repo.git_cloud == GitCloudService.GITHUB:
            if git_release is None:
                raise IOError('Could not create release')
            return git_release.tag_name, git_release.html_url
        else:
            raise ValueError(
                f'Unknown git cloud service {component.repo.git_cloud}')

    def release_component_github(self):
        pass

    def release_component_bitbucket(
            self,
            release: NovaRelease,
            component: NovaComponent,
            branch: str,
            is_hotix: bool = False):
        with TemporaryDirectory() as sources_dir:
            print(f"Cloning repository into [{sources_dir}]...")
            repo = Repo.clone_from(
                component.repo.url, sources_dir, branch=branch)
            # TODO: move file name to configuration
            changelog_path = fs.search_file(sources_dir, 'CHANGELOG.md')
            if changelog_path is None:
                raise FileNotFoundError('CHANGELOG.md file not found')
            version = fs.extract_latest_version_from_changelog(changelog_path)
            if version is None:
                raise ValueError(
                    f'Could not extract version from {changelog_path}')

            parsed_version = None
            try:
                parsed_version = parse(version)
            except InvalidVersion as ex:
                raise ValueError('Could not parse version from CHANGELOG.md,' +
                                 ' it should be in PEP 440 format') from ex

            if is_hotix:
                v_str = f'{parsed_version.major}.{parsed_version.minor}.{parsed_version.micro+1}'
                parsed_version = Version(v_str)
            else:
                v_str = f'{parsed_version.major}.{parsed_version.minor+1}.{0}'
                parsed_version = Version(v_str)

            relese_notes_title = f'## {str(parsed_version)} {release.title} ({datetime.now().strftime("%B %d, %Y")})'
            release_notes = component.get_release_notes(None, None)
            with open(changelog_path, 'r+', encoding='utf-8') as changelog_file:
                content = changelog_file.read()
                changelog_file.seek(0, 0)
                changelog_file.write(relese_notes_title +
                                     '\n' + release_notes + '\n\n' + content)
            # todo: add deployment section if there is any jira task with deployment comment
            call([self.__text_editor, changelog_path])
            input('Press Enter to continue when you are done' +
                  ' with editing file in external editor ...')

            csproj_file_paths = fs.search_files_with_ext(sources_dir, 'csproj')
            csproj_file_paths_with_version = fs.search_files_with_content(
                csproj_file_paths, '<Version>')
            if len(csproj_file_paths_with_version) == 0:
                raise FileNotFoundError(
                    'Could not find csproj file with version to update')
            print(
                'There are following csproj files with version found. Please choose the one to update:')
            csproj_file_path = console.choose_from_or_skip(
                csproj_file_paths_with_version)
            if csproj_file_path is None:
                # skip selection
                return
            new_file_content = None
            with open(csproj_file_path, 'r', encoding='utf-8') as csproj_file:
                content = csproj_file.read()
                new_file_content = re.sub(
                    r'<Version>(.*?)<\/Version>',
                    f'<Version>{str(parsed_version)}</Version>', content)
            with open(csproj_file_path, 'w+', encoding='utf-8') as csproj_file:
                csproj_file.write(new_file_content)
            # todo: add only csproj and changelog files
            repo.git.add('.')
            commit_message = f'Version {str(parsed_version)}'
            repo.index.commit(commit_message)
            tag_name = f'nova-{str(parsed_version)}'
            tag_message = f'Version {tag_name} release'
            repo.create_tag(tag_name, message=tag_message)
            origin = repo.remote(name='origin')
            origin.push()
            origin.push(tags=True)
