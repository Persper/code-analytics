from typing import Iterable

from persper.analytics2.abstractions.analyzers import ICommitAnalyzer, IPostAnalyzer
from persper.analytics2.abstractions.repository import ICommitRepository


class MetaAnalyzer():
    """
    Coordinates `ICommitAnalyzer` and `IPostAnalyzer` implementation, doing analysis through the commit history.
    """
    def __init__(self, history_provider: ICommitRepository,
                 commit_analyzers: Iterable[ICommitAnalyzer], post_analyzers: Iterable[IPostAnalyzer],
                 origin_commit: str = None, terminal_commit: str = "HEAD",
                 first_parent_only: bool = False,
                 analyzed_commits: Iterable[str] = None):
        if not isinstance(history_provider, ICommitRepository):
            raise ValueError("Expect ICommitRepository instance for history_provider.")
        # do necessary defensive copies
        self._history_provider = history_provider
        self._commit_analyzers = list(commit_analyzers)
        self._post_analyzers = list(post_analyzers)
        self._origin_commit = origin_commit
        self._terminal_commit = terminal_commit
        self._first_parent_only = first_parent_only
        self._analyzed_commits = set(analyzed_commits) if analyzed_commits else set()

    @property
    def origin_commit(self):
        return self._origin_commit

    @origin_commit.setter
    def origin_commit(self, value: str):
        self._origin_commit = value

    @property
    def terminal_commit(self):
        return self._terminal_commit

    @terminal_commit.setter
    def terminal_commit(self, value: str):
        self._terminal_commit = value

    @property
    def first_parent_only(self):
        return self._first_parent_only

    @first_parent_only.setter
    def first_parent_only(self, value: bool):
        self._first_parent_only = value

    def analyze(self, max_commits: int = 100):
        pass
