"""
Module for fake classes used in tests.
"""


from datetime import date


class FakeConfig:
    """Configuration object for fakes"""

    def __init__(self, tags_count: int = 5, create_release: bool = True):
        """
        :param tags_count: number of fake tags to create
        :param create_release: whether to create a fake release
        """
        if tags_count < 1:
            raise ValueError("Tags count must be greater than zero")

        self.tags_count = tags_count
        self.create_release = create_release


class FakeGitHub:
    """Fake GitHub API client."""

    def __init__(self, config: FakeConfig):
        self.__config = config

    def get_repo(self, _):
        return FakeRepository(self.__config)


class FakeGitTag:
    """Fake GitHub tag."""

    def __init__(self, tag: str, sha: str):
        self.tag = tag
        self.sha = sha


class FakeGitAuthor:
    """Fake GitHub author."""

    def __init__(self, name: str):
        self.name = name


class FakeGitCommit:
    """Fake GitHub commit."""

    def __init__(self, last_modified: str, author: FakeGitAuthor):
        self.last_modified = last_modified
        self.author = author


class FakeCommit:
    """Fake GitHub commit."""

    def __init__(self, commit: FakeGitCommit):
        self.commit = commit
        self.sha = "fake_sha"


class FakeTag:
    """Fake GitHub tag."""

    def __init__(self, name: str, commit: FakeCommit):
        self.name = name
        self.commit = commit


class FakeBranch:
    """Fake GitHub branch."""

    def __init__(self, commit: FakeCommit, branch_name: str):
        self.commit = commit
        self.branch = branch_name


class FakeGitRelease:
    """Fake GitHub release."""

    def __init__(self, tag: str, name: str, message: str):
        self.tag = tag
        self.name = name
        self.message = message


class FakeRepository:
    """
    Fake GitHub repository.

    Initial tags are created in the range from 1 to 10.
    """

    def __init__(self, config: FakeConfig):
        self.__config = config
        self.__tags = [
            FakeTag(
                str(i),
                FakeCommit(
                    FakeGitCommit(
                        date.today().strftime("%Y-%m-%d"),
                        FakeGitAuthor(f"Author {i}"),
                    )
                ),
            )
            for i in range(1, self.__config.tags_count + 1)
        ]

    def get_tags(self) -> list[FakeTag]:
        return self.__tags

    def get_branch(self, branch) -> FakeBranch:
        return FakeBranch(
            FakeCommit(FakeGitCommit("", FakeGitAuthor(""))), branch
        )

    def create_git_tag(self, tag_name, _, sha, tag_type) -> FakeGitTag:
        self.__tags.append(
            FakeTag(tag_name, FakeCommit(FakeGitCommit("", FakeGitAuthor(""))))
        )
        return FakeGitTag(tag_name, sha)

    def create_git_ref(self, ref, sha):
        pass

    def create_git_release(self, tag, name, message) -> FakeGitRelease | None:
        return (
            FakeGitRelease(tag, name, message)
            if self.__config.create_release
            else None
        )
