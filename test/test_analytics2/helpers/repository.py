import logging
from datetime import datetime, timezone
from itertools import islice
from random import randint

from persper.analytics2.abstractions.repository import (FileDiffOperation,
                                                        ICommitInfo,
                                                        ICommitRepository,
                                                        IFileDiff)

_logger = logging.getLogger(__file__)


def test_repository_history_provider(rhp: ICommitRepository):
    assert rhp
    # We enumerate from the beginning
    commits = list(islice(rhp.enum_commits(None, "HEAD"), 1000))
    print("Retrieved {} commits.".format(len(commits)))
    if len(commits) < 2:
        _logger.warn("Skipped commit tests because there are too few commits in the repository.")
        return
    # First commit should not have parent
    assert len(commits[0].parents) == 0, "First commit has parent. Are you using shallow-cloned repository?"
    seenCommits = set()
    for c in commits:
        assert isinstance(c, ICommitInfo)
        assert isinstance(c.hexsha, str)
        # We should see every commit only once
        assert c.hexsha not in seenCommits
        seenCommits.add(c.hexsha)
        assert all((isinstance(c1, ICommitInfo) for c1 in c.parents))
        parentsList = [p.hexsha for p in c.parents]
        parents = set(parentsList)
        # Parents should not duplicate
        assert len(parents) == len(parentsList)
        # Topological order
        assert parents.issubset(seenCommits)
        # Sanity check
        assert "@" in c.author_email
        assert "@" in c.committer_email
        assert datetime(1990, 1, 1, tzinfo=timezone.utc) <= c.authored_time <= datetime(2200, 1, 1, tzinfo=timezone.utc)
        assert datetime(1990, 1, 1, tzinfo=timezone.utc) <= c.committed_time <= datetime(
            2200, 1, 1, tzinfo=timezone.utc)
        assert c.authored_time <= c.committed_time

    def getPathTuple(diff: IFileDiff):
        return (diff.old_file.path if diff.old_file else "",
                diff.new_file.path if diff.new_file else "")

    def reverseFileDiffOperation(op: FileDiffOperation):
        result = FileDiffOperation.Unchanged
        if op & FileDiffOperation.Added:
            result |= FileDiffOperation.Deleted
        if op & FileDiffOperation.Deleted:
            result |= FileDiffOperation.Added
        if op & FileDiffOperation.Modified:
            result |= FileDiffOperation.Modified
        if op & FileDiffOperation.Renamed:
            result |= FileDiffOperation.Renamed
        return result

    prevCommit: ICommitInfo = None
    for c in islice(commits, 0, 100):
        # Diff with self
        diff = list(c.diff_from(c))
        assert len(diff) == 0
        if prevCommit != None:
            print("Enter commit: prev={}, current={}".format(prevCommit, c))
            diff = list(c.diff_from(prevCommit))
            diffr = list(prevCommit.diff_from(c))
            assert len(diff) == len(diffr)
            diff.sort(key=getPathTuple)
            diffr.sort(key=lambda d: getPathTuple(d)[::-1])
            print("Commit diffs={}".format(len(diff)))
            for d, dr in zip(diff, diffr):
                assert isinstance(d, IFileDiff)
                assert isinstance(dr, IFileDiff)
                print("File diff [d]: ", d)
                print("File diff [dr]: ", dr)
                assert (d.old_file != None) == (dr.new_file != None)
                assert (d.new_file != None) == (dr.old_file != None)
                assert getPathTuple(dr) == getPathTuple(d)[::-1]
                assert d.operation == reverseFileDiffOperation(dr.operation)
                if d.old_file:
                    assert d.old_file.size == dr.new_file.size
                if d.new_file:
                    assert d.new_file.size == dr.old_file.size
        prevCommit = c
