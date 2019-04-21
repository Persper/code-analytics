from abc import ABC, abstractclassmethod, abstractproperty
from typing import IO, Iterable, NoReturn

from aenum import Enum


class CommitAnalysisStopReason(Enum):
    _init_ = "value __doc__"
    ReachedTerminalCommit = 0, "Terminal commit has reached."
    ReachedMaximumCommits = 1, "Maximum commit analysis count has reached."
    FatalError = 2, "An exception occurred during analyzing a commit."
    Abort = 3, "User or other external signal aborts the analysis before its completion."


class AnalysisStatus():
    """
    An immutable status snapshot of meta analysis. Usually used to provide status information for `IPostAnalyzer`.
    """

    def __init__(self, stop_reason: CommitAnalysisStopReason, exception: Exception,
                 origin_commit_ref: str, terminal_commit_ref: str,
                 analyzed_commits_ref: Iterable[str], last_commit_ref: str):
        self._stop_reason = stop_reason
        self._exception = exception
        self._origin_commit_ref = origin_commit_ref
        self._terminal_commit_ref = terminal_commit_ref
        self._analyzed_commits_ref = analyzed_commits_ref
        self._last_commit_ref = last_commit_ref

    @property
    def stop_reason(self):
        return self._stop_reason

    @property
    def exception(self):
        """
        Gets the Exception that caused failure of analysis.
        """
        return self._exception

    @property
    def origin_commit_ref(self):
        """
        Gets the commit ref of intended analysis origin.
        """
        return self._origin_commit_ref

    @property
    def terminal_commit_ref(self):
        """
        Gets the commit ref of intended analysis terminal (inclusive).
        """
        return self._terminal_commit_ref

    @property
    def analyzed_commits_ref(self):
        """
        Gets a list of commits that are actually analyzed completely.
        remarks
            The list will exclude all the commits that are skipped or failed to analyze.
        """
        return self._analyzed_commits_ref

    @property
    def last_commit_ref(self):
        """
        Gets the the last commit ref being analyzed before the analysis stops.
        remarks
            If there are fatal error analyzing the commit, this member should be the commit that causes the error.
        """
        return self._last_commit_ref


class ICommitAnalyzer(ABC):
    """
    Provides functionality for analyzing a single commit.
    remarks
        The implementation will decide where to put the analysis result.
    """
    @abstractclassmethod
    def analyze(self, commit_ref: str) -> None:
        pass


class IPostAnalyzer(ABC):
    """
    Provides functionality for doing post-analysis after the commit analysis ends due to
    completion or exception.
    """
    @abstractclassmethod
    def analyze(self, status: AnalysisStatus) -> None:
        pass
