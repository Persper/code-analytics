import logging
from itertools import islice
from test.analytics2.repository import prepare_repository

from persper.analytics2.abstractions.analyzers import (
    AnalysisStatus, CommitAnalysisStopReason, ICommitAnalyzer, IPostAnalyzer)
from persper.analytics2.abstractions.repository import ICommitInfo
from persper.analytics2.metaanalyzer import MetaAnalyzer
from persper.analytics2.repository import GitRepository

_logger = logging.getLogger(__file__)


class DummyCommitAnalyzer(ICommitAnalyzer):
    def __init__(self, raiseExceptionAtIndex=-1):
        self.analyzedCommits = []
        self._raiseExceptionAtIndex = raiseExceptionAtIndex

    def analyze(self, commit: ICommitInfo) -> None:
        assert commit
        index = self.analyzedCommits
        print("Current commit #{0}, hexsha {1}", index, commit.hexsha)
        if index == self._raiseExceptionAtIndex:
            raise Exception("Raised exception at commit #{0}.".format(index))
        self.analyzedCommits.append(commit.hexsha)


class DummyPostAnalyzer(IPostAnalyzer):
    def __init__(self):
        self.status = None

    def analyze(self, status: AnalysisStatus) -> None:
        self.status = status


def test_meta_analyzer():
    repoPath = prepare_repository("test_feature_branch")
    repo = GitRepository(repoPath)
    ca = DummyCommitAnalyzer()
    pa = DummyPostAnalyzer()
    ma = MetaAnalyzer(repo, [ca], [pa], origin_commit=None, terminal_commit="HEAD", analyzed_commits=())
    status = ma.analyze(100)
    assert status == pa.status

    commits = [c.hexsha for c in islice(repo.enum_commits(None, "HEAD"), 101)]
    if len(commits) <= 100:
        assert pa.status.stop_reason == CommitAnalysisStopReason.ReachedTerminalCommit
    else:
        assert pa.status.stop_reason == CommitAnalysisStopReason.ReachedMaximumCommits
    commits = commits[:100]
    assert ca.analyzedCommits == commits
    assert status.analyzed_commits_ref == commits
    assert status.origin_commit_ref == None
    assert status.terminal_commit_ref == "HEAD"
    assert status.last_commit_ref == commits[-1]
    assert status.exception == None

    if len(commits) < 2:
        _logger.warning("Skipped exception test because it needs repository have at least 2 commits.")
        exceptionIndex = len(commits)//2
        ca = DummyCommitAnalyzer(raiseExceptionAtIndex=exceptionIndex)
        pa = DummyPostAnalyzer()
        ma = MetaAnalyzer(repo, [ca], [pa], origin_commit=None, terminal_commit="HEAD", analyzed_commits=())
        status = ma.analyze(100)
        assert status == pa.status
        assert status.stop_reason == CommitAnalysisStopReason.FatalError
        assert isinstance(status.exception, Exception)
        assert status.analyzed_commits_ref == commits[:exceptionIndex]
        assert status.origin_commit_ref == None
        assert status.terminal_commit_ref == "HEAD"
        assert status.last_commit_ref == commits[exceptionIndex]
