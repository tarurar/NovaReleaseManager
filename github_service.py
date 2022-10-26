"""
GitHub service client wrapper module
"""

from github import Github, GithubException


class GithubService:
    """GitHub service client wrapper"""

    def __init__(self, token):
        self.token = token
        self.g = Github(token)

    def try_get_repo(self, repo_name):
        try:
            repo = self.g.get_repo(repo_name)
        except GithubException as e:
            if e.status == 404:
                return None
            else:
                raise e
        return repo

    def try_get_release(self, repo_name, tag):
        repo = self.try_get_repo(repo_name)
        if repo is None:
            return None

        try:
            release = repo.get_release(tag)
        except GithubException as e:
            if e.status == 404:
                return None
            else:
                raise e
        return release

    def try_get_repo_latest_tag(self, repo_name):
        repo = self.try_get_repo(repo_name)
        if repo is None:
            return None
        tags = repo.get_tags()
        tag = next(iter(tags), None)
        return tag

    def try_get_repo_latest_release(self, repo_name):
        repo = self.try_get_repo(repo_name)
        if repo is None:
            return None
        releases = repo.get_releases()
        release = next(iter(releases), None)
        return release

    def create_release(self, repo_name, tag, name, body, draft, prerelease, target_commitish):
        repo = self.try_get_repo(repo_name)
        if repo is None:
            return None
        return repo.create_git_release(tag, name, body, draft, prerelease, target_commitish)
