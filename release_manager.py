"""
The release manager is responsible for managing the release process.
"""

import logging

from git import Tag, Repo
from github import Github
from jira import JIRA, JIRAError
from jira.resources import Version
from tempfile import TemporaryDirectory
from subprocess import call
from packaging.version import parse, Version, InvalidVersion
from datetime import datetime
import re


import github_utils as gu
import jira_utils as ju
import fs_utils as fs
import text_utils as txt
from core.cvs import GitCloudService
from core.nova_component import NovaComponent
from core.nova_release import NovaRelease
from core.nova_status import Status


class ReleaseManager:
    """The release manager is responsible for managing the release process."""
    # todo: add dependant client packages update validation.
    # Common issue: package updated but not mentioned in release notes

    default_text_editor = 'vim'

    def __init__(self, jira_client: JIRA, github_client: Github, text_editor: str) -> None:
        self.__j = jira_client
        self.__g = github_client
        self.__text_editor = text_editor if text_editor is not None else ReleaseManager.default_text_editor

    def __get_jira_issues(self, project: str, fix_version: str, cmp='') -> list:
        result = []
        i = 0
        chunk_size = 50

        jql = ju.build_jql(project, fix_version, cmp)
        while True:
            try:
                issues = self.__j.search_issues(
                    jql, maxResults=chunk_size, startAt=i)
            except JIRAError:
                return []
            i += chunk_size
            result += issues.iterable
            if i >= issues.total:
                break
        return result

    def compose(self, project: str, version: str, delivery: str) -> NovaRelease:
        """Get release by project, version and delivery"""
        release = NovaRelease(project, version, delivery)

        components = [ju.parse_jira_component(cmp)
                      for cmp in self.__j.project_components(project)]

        release_jira_issues = self.__get_jira_issues(project, release)

        for component in components:
            component_jira_issues = filter(
                lambda i, cname=component.name: ju.filter_jira_issue(i, cname),
                release_jira_issues)
            component_tasks = [ju.parse_jira_issue(issue)
                               for issue in component_jira_issues]
            if len(component_tasks) > 0:
                component.add_tasks(component_tasks)
                release.add_component(component)

        return release

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
            raise Exception('Component is not specified')

        if component.status == Status.DONE:
            raise Exception(
                f'Component [{component.name}] is already released')

        if component.status != Status.READY_FOR_RELEASE:
            raise Exception(
                f'Component [{component.name}] is not ready for release')
        
        if component.repo.git_cloud == GitCloudService.BITBUCKET:
            # TODO: git cli has to be installed and configured to access bitbucket and to push into master
            self.release_component_bitbucket(release, component, branch)
        elif component.repo.git_cloud == GitCloudService.GITHUB:
            # GitHub specific code
            # get an instance of the remote repository
            repo_url = gu.get_github_compatible_repo_address(component.repo.url)
            repo = self.__g.get_repo(repo_url)
            if repo is None:
                raise Exception(f'Cannot get repository {component.repo.url}')

            # this call return a list of Tag class instances (not GitTag class instances)
            # choosing a tag for the release
            tags = repo.get_tags()
            top5_tags = list(tags)[:5]
            print(f'Please, choose a tag to release component [{component.name}]')
            tag = ReleaseManager.choose_existing_tag(top5_tags)
            if tag is None:
                tag_name = ReleaseManager.input_tag_name()
                if tag_name is None:
                    return
                sha = repo.get_branch(branch).commit.sha
                git_tag_name = repo.create_git_tag(
                    tag_name, release.title, sha, 'commit').tag
            else:
                git_tag_name = tag.name

            # choosing a tag of the previous release
            print(
                f'Please, choose a tag of previous component [{component.name}] release')
            previous_tag = ReleaseManager.choose_existing_tag(top5_tags)
            if previous_tag is None:
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
                        'Auto-detected previous release tag: %s', previous_tag_name)
            else:
                previous_tag_name = previous_tag.name

            # creating a release
            git_release = repo.create_git_release(
                git_tag_name,
                release.title,
                component.get_release_notes(previous_tag_name, git_tag_name))
            if git_release is None:
                raise Exception(f'Could not create release for tag {git_tag_name}')

        # moving jira issues to DONE
        for task in component.tasks:
            try:
                self.__j.transition_issue(
                    task.name,
                    'Done',
                    comment=f'{release.title} released')
            except JIRAError as error:
                logging.warning(
                    'Could not transition issue %s due to error: %s',
                    task.name,
                    error.text)

        if component.repo.git_cloud == GitCloudService.BITBUCKET:
            return 'Bitbucket tag to be', 'Bitbucket tah link to be'
        elif component.repo.git_cloud == GitCloudService.GITHUB:
            return git_release.tag_name, git_release.html_url

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
            repo = Repo.clone_from(component.repo.url, sources_dir, branch=branch)
            # TODO: move file name to configuration
            changelog_path = fs.search_file(sources_dir, 'CHANGELOG.md')
            if changelog_path is None:
                raise Exception('CHANGELOG.md file not found')
            version = self.extract_latest_version_from_changelog(changelog_path)
            if version is None:
                raise Exception('Could not extract version from CHANGELOG.md')
            
            parsed_version = None
            try:
                parsed_version = parse(version)
            except InvalidVersion:
                raise Exception('Could not parse version from CHANGELOG.md, it should be in PEP 440 format')
            
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
                changelog_file.write(relese_notes_title + '\n' + release_notes + '\n\n' + content)
            # todo: add deployment section if there is any jira task with deployment comment
            call([self.__text_editor, changelog_path])
            input(f'Press Enter to continue when you are done with editing file in external editor ...')

            csproj_file_paths = fs.search_files_with_ext(sources_dir, 'csproj')
            csproj_file_paths_with_version = fs.search_files_with_content(csproj_file_paths, '<Version>')
            if len(csproj_file_paths_with_version) == 0:
                raise Exception('Could not find csproj file with version to update')
            print('There are following csproj files with version found. Please choose the one to update:')
            csproj_file_path = ReleaseManager.choose_existing_file_path(csproj_file_paths_with_version)
            if csproj_file_path is None:
                return
            new_file_content = None
            with open(csproj_file_path, 'r', encoding='utf-8') as csproj_file:
                content = csproj_file.read()
                new_file_content = re.sub(r'<Version>(.*?)<\/Version>', f'<Version>{str(parsed_version)}</Version>', content)
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

    
    def extract_latest_version_from_changelog(self, changelog_path: str) -> str:
        with open(changelog_path, 'r', encoding='utf-8') as changelog_file:
            for line in changelog_file:
                version = txt.try_extract_nova_component_version(line)
                if version is not None:
                    return version
                return None

    def preview_component_release(
            self,
            release: NovaRelease,
            component: NovaComponent):
        """Prints release information for the component"""
        print('Please, review the compone˝nt release information:')
        print('=' * 80)
        print(f'Component: {component.name}.')
        print(f'Version: {release.title}.')
        print('Tasks:')
        for task in component.tasks:
            task_release_notes = task.get_release_notes()
            print(task_release_notes)

    def can_release_version(self, project: str, version: str, delivery: str) -> bool:
        """Checks if release can be marked as DONE"""
        release = self.compose(project, version, delivery)
        if release.can_release_version():
            jira_version = self.__j.get_project_version_by_name(
                project=project, version_name=release.title)
            return ReleaseManager.can_release_jira_version(jira_version)
        return False

    def release_version(self, release: NovaRelease):
        """Marks release as DONE"""
        if release is None:
            raise Exception('Release is not specified')
        jira_version = self.__j.get_project_version_by_name(
            project=release.project, version_name=release.title)
        if jira_version is None:
            raise Exception(f'Cannot find JIRA version {release.title}')
        jira_version.update(released=True)

    @classmethod
    def can_release_jira_version(cls, version: Version) -> bool:
        """Checks if Jira version can be released"""
        if version is None:
            return False
        if version.archived:
            return False
        if version.released:
            return False
        return True

    @classmethod
    def input_tag_name(cls) -> str:
        """Input tag"""
        tag_name = input('Enter new tag or just press `q` to quit: ')
        if tag_name == 'q':
            return None
        if tag_name is None or tag_name.strip() == '':
            return cls.input_tag_name()
        return tag_name

    @classmethod
    def choose_existing_tag(cls, existing_tags: list[Tag]) -> Tag:
        """Choose a tag from existing tags"""
        if not existing_tags:
            return None

        tags_view = {}
        for index, tag in enumerate(existing_tags):
            view_index = index + 1
            tags_view[view_index] = tag
            print(
                f'{view_index}: {tag.name} @ {tag.commit.commit.last_modified} by {tag.commit.commit.author.name}')

        selection = input(
            "\nEnter either tag position number from " +
            "the list or just press enter for new tag: ")
        if selection is None or selection.strip() == '':
            return None

        if selection.isdigit():
            tag_position = int(selection)
            if tag_position in tags_view:
                return tags_view[tag_position]
            else:
                logging.warning('Tag number is not in the list')
                return cls.choose_existing_tag(existing_tags)
        else:
            return cls.choose_existing_tag(existing_tags)
        
    @classmethod
    def choose_existing_file_path(cls, existing_file_paths) -> str:
        if not existing_file_paths:
            return None
        
        file_paths_view = {}
        for index, file_path in enumerate(existing_file_paths):
            view_index = index + 1
            file_paths_view[view_index] = file_path
            print(f'{view_index}: {file_path}')

        selection = input(
            "\nEnter file path position number from the list or just press enter to skip: ")
        if selection is None or selection.strip() == '':
            return None
        
        if selection.isdigit():
            file_path_position = int(selection)
            if file_path_position in file_paths_view:
                return file_paths_view[file_path_position]
            else:
                logging.warning('File path number is not in the list')
                return cls.choose_existing_file_path(existing_file_paths)
        else:
            return cls.choose_existing_file_path(existing_file_paths)
