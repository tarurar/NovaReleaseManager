"""
Module for fake classes used in tests.
"""


from datetime import date
from dataclasses import dataclass


@dataclass
class FakeConfig:
    """Configuration object for fakes"""

    tags_count: int = 5
    create_release: bool = True

    def __post_init__(self):
        if self.tags_count < 1:
            raise ValueError("Tags count must be greater than zero")


@dataclass
class FakeGitHub:
    """Fake GitHub API client."""

    config: FakeConfig

    def get_repo(self, _):
        return FakeRepository(self.config)


@dataclass
class FakeGitTag:
    """Fake GitHub tag."""

    tag: str
    sha: str


@dataclass
class FakeGitAuthor:
    """Fake GitHub author."""

    name: str


@dataclass
class FakeGitCommit:
    """Fake GitHub commit."""

    last_modified: str
    author: FakeGitAuthor


@dataclass
class FakeCommit:
    """Fake GitHub commit."""

    commit: FakeGitCommit
    sha: str = "fake_sha"


@dataclass
class FakeTag:
    """Fake GitHub tag."""

    name: str
    commit: FakeCommit


@dataclass
class FakeBranch:
    """Fake GitHub branch."""

    commit: FakeCommit
    branch: str


@dataclass
class FakeGitRelease:
    """Fake GitHub release."""

    tag: str
    name: str
    message: str


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

    # pylint: disable=unused-argument
    def create_git_tag(self, tag_name, message, sha, tag_type) -> FakeGitTag:
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
