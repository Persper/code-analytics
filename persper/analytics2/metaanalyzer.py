import logging
import re
import traceback
from typing import Iterable

from persper.analytics2.abstractions.analyzers import (
    AnalysisStatus, CommitAnalysisStopReason, ICommitAnalyzer, IPostAnalyzer)
from persper.analytics2.abstractions.repository import (ICommitInfo,
                                                        ICommitRepository,
                                                        repr_hexsha)

_logger = logging.getLogger(__file__)
_whitespace_re = re.compile(r"\s+")


class MetaAnalyzer():
    """
    Coordinates `ICommitAnalyzer` and `IPostAnalyzer` implementation, doing analysis through the commit history.
    params
        origin_commit, terminal_commit: See `ICommitRepository.enum_commits` for details.
    """

    def __init__(self, repository: ICommitRepository,
                 commit_analyzers: Iterable[ICommitAnalyzer], post_analyzers: Iterable[IPostAnalyzer],
                 origin_commit: str = None, terminal_commit: str = "HEAD",
                 analyzed_commits: Iterable[str] = None):
        if not isinstance(repository, ICommitRepository):
            raise ValueError("Expect ICommitRepository instance for repository.")
        # do necessary defensive copies
        self._repository = repository
        self._commit_analyzers = list(commit_analyzers)
        self._post_analyzers = list(post_analyzers)
        self._origin_commit = origin_commit
        self._terminal_commit = terminal_commit
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

    def analyze(self, max_commits: int = 100):
        _logger.info("Start analyzing: %s..%s, max_commits=%d .",
                     self._origin_commit, self._terminal_commit, max_commits)
        analyzedCommits = []
        currentSkippedCommits = 0
        currentSkippedFirstCommit = None
        currentSkippedLastCommit = None
        stopReason = CommitAnalysisStopReason.ReachedTerminalCommit
        lastCommitRef = None
        # XXX determine whether we need to add this into AnalysisStatus
        failedAnalyzer = None
        failedAnalyzerException = None
        for commit in self._repository.enum_commits(self._origin_commit, self._terminal_commit):
            assert isinstance(commit, ICommitInfo)
            if len(analyzedCommits) >= max_commits:
                _logger.info("Max analyzed commits reached.")
                stopReason = CommitAnalysisStopReason.ReachedMaximumCommits
                break
            lastCommitRef = commit.hexsha
            # Skip commits we have already analyzed previously
            if lastCommitRef in self._analyzed_commits:
                currentSkippedLastCommit = lastCommitRef
                if currentSkippedFirstCommit == None:
                    currentSkippedCommits = 0
                    currentSkippedFirstCommit = currentSkippedLastCommit
                currentSkippedCommits += 1
                continue
            if currentSkippedFirstCommit != None:
                _logger.info("Skipped %s analyzed commits: %s..%s .",
                             currentSkippedCommits, currentSkippedFirstCommit, currentSkippedLastCommit)
                currentSkippedFirstCommit = None
            # Analyze commit
            if _logger.getEffectiveLevel <= logging.INFO:
                briefMessage = commit.message
                trimmed = len(briefMessage) > 50
                briefMessage = re.sub(_whitespace_re, " ", briefMessage[:60])[:47]
                if trimmed:
                    briefMessage += "..."
                _logger.info("Analyzing commit [%s]: %s", repr_hexsha(lastCommitRef), briefMessage)
            analyzer = None
            analyzerIndex = 0
            try:
                for analyzer in self._commit_analyzers:
                    assert isinstance(analyzer, ICommitAnalyzer)
                    _logger.debug("Analyzing with [%d]: %s .", analyzerIndex, analyzer)
                    analyzer.analyze(commit)
                    analyzerIndex += 1
                if _logger.getEffectiveLevel <= logging.DEBUG:
                    _logger.debug("Finished analyzing commit [%s].", repr_hexsha(lastCommitRef))
            except Exception as ex:
                _logger.error("Failed to analyze commit [%s] with analyzer [%d][%s].\n%s",
                              lastCommitRef, analyzerIndex, analyzer, ex)
                failedAnalyzer = analyzer
                failedAnalyzerException = ex
                stopReason = CommitAnalysisStopReason.FatalError
                break
            analyzedCommits.append(lastCommitRef)
            self._analyzed_commits.add(lastCommitRef)
        # Post analysis
        if self._post_analyzers:
            analyzer = None
            analyzerIndex = 0
            status = AnalysisStatus(stop_reason=stopReason, exception=failedAnalyzerException,
                                    origin_commit_ref=self._origin_commit, terminal_commit_ref=self._terminal_commit,
                                    analyzed_commits_ref=analyzedCommits, last_commit_ref=lastCommitRef)
            try:
                for analyzer in self._post_analyzers:
                    assert isinstance(analyzer, IPostAnalyzer)
                    _logger.debug("Post-analyzing with [%d]: %s .", analyzerIndex, analyzer)
                    analyzer.analyze(status)
                    analyzerIndex += 1
            except Exception as ex:
                _logger.error("Failed during post-analysis with analyzer [%d][%s].\n%s",
                              analyzerIndex, analyzer, ex)
                # We can do nothing about it. Crash the caller.
                raise
