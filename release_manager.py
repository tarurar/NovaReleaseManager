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
import github_utils as gu
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
        self.__g = github_client
        self.__text_editor = text_editor if text_editor is not None else ReleaseManager.default_text_editor

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
            # GitHub specific code
            # get an instance of the remote repository
            repo_url = gu.get_github_compatible_repo_address(
                component.repo.url)
            repo = self.__g.get_repo(repo_url)
            if repo is None:
                raise IOError(f'Cannot get repository {component.repo.url}')

            # this call return a list of Tag class instances
            # (not GitTag class instances)
            # choosing a tag for the release
            tags = repo.get_tags()
            top5_tags = list(tags)[:5]
            top5_tag_names = list(map(
                lambda
                t:
                f'{t.name} @ {t.commit.commit.last_modified} by {t.commit.commit.author.name}',
                top5_tags))
            print(
                f'Please, choose a tag to release component [{component.name}]')
            tag_index = console.choose_from_or_skip(top5_tag_names)
            if tag_index is None:
                tag_name = console.input_tag_name()
                if tag_name is None:
                    return '', ''
                sha = repo.get_branch(branch).commit.sha
                git_tag_name = repo.create_git_tag(
                    tag_name, release.title, sha, 'commit').tag
            else:
                git_tag_name = top5_tags[tag_index].name

            # choosing a tag of the previous release
            print(
                f'Please, choose a tag of previous component [{component.name}] release')

            previous_tag_index = console.choose_from_or_skip(top5_tag_names)
            if previous_tag_index is None:
                logging.warning(
                    'Previous release tag was not specified, auto-detection will be used')
                auto_detected_previous_tag_list = list(filter(
                    lambda t: t.name != git_tag_name, top5_tags))
                if len(auto_detected_previous_tag_list) > 0:
                    previous_tag_name = auto_detected_previous_tag_list[0].name
                else:
                    previous_tag_name = ''
                if not previous_tag_name:
                    logging.warning(
                        'Auto-detection failed, changelog url will be empty')
                else:
                    logging.info(
                        'Auto-detected previous release tag: %s',
                        previous_tag_name)
            else:
                previous_tag_name = top5_tags[previous_tag_index].name

            # creating a release
            git_release = repo.create_git_release(
                git_tag_name,
                release.title,
                component.get_release_notes(previous_tag_name, git_tag_name))
            if git_release is None:
                raise IOError(
                    f'Could not create release for tag {git_tag_name}')

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
