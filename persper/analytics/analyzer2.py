import asyncio
import collections.abc
import logging
import re
import time
from abc import ABC
from typing import List, Optional, Set, Union

from git import Commit, Diff, DiffIndex, Repo

from persper.analytics.commit_classifier import CommitClassifier
from persper.analytics.git_tools import diff_with_commit, get_contents
from persper.analytics.graph_server import CommitSeekingMode, GraphServer
from persper.analytics.score import commit_overall_scores

_logger = logging.getLogger(__name__)


class Analyzer:
    def __init__(self, repositoryRoot: str, graphServer: GraphServer,
                 terminalCommit: str = 'HEAD',
                 firstParentOnly: bool = False,
                 commit_classifier: Optional[CommitClassifier] = None):
        self._repositoryRoot = repositoryRoot
        self._graphServer = graphServer
        self._repo = Repo(repositoryRoot)
        self._originCommit: Commit = None
        self._terminalCommit: Commit = self._repo.rev_parse(terminalCommit)
        self._firstParentOnly = firstParentOnly
        self._visitedCommits = set()
        self._s_visitedCommits = _ReadOnlySet(self._visitedCommits)
        self._observer: AnalyzerObserver = emptyAnalyzerObserver
        self._commit_classifier = commit_classifier
        self._clf_results: Dict[str, List[float]] = {}

    def __getstate__(self):
        state = self.__dict__.copy()
        state.pop("_repo", None)
        state.pop("_s_visitedCommits", None)
        state["_originCommit"] = self._originCommit.hexsha if self._originCommit else None
        state["_terminalCommit"] = self._terminalCommit.hexsha if self._terminalCommit else None
        state.pop("_observer", None)
        return state

    def __setstate__(self, state):
        self.__dict__.update(state)
        self._repo = Repo(self._repositoryRoot)
        self.originCommit = state["_originCommit"]
        self.terminalCommit = state["_terminalCommit"]
        self._s_visitedCommits = _ReadOnlySet(self._visitedCommits)
        self._observer: AnalyzerObserver = emptyAnalyzerObserver

    @property
    def graphServer(self):
        return self._graphServer

    @property
    def observer(self):
        """
        The AnalyzerObserver used to observe current Analyzer.
        """
        return self._observer

    @observer.setter
    def observer(self, value):
        self._observer = value or emptyAnalyzerObserver

    @property
    def originCommit(self):
        """
        Gets/sets the first commit to visit. (exclusive)
        Use None to start visiting from the first commit.
        """
        return self._originCommit

    @originCommit.setter
    def originCommit(self, value: Union[Commit, str]):
        self._originCommit = self._repo.commit(value) if value else None

    @property
    def terminalCommit(self):
        """
        Gets/sets the last commit to visit. (inclusive)
        """
        return self._terminalCommit

    @terminalCommit.setter
    def terminalCommit(self, value: Union[Commit, str]):
        self._terminalCommit = self._repo.commit(value)

    @property
    def firstParentOnly(self):
        """
        Whether to only visit each commit's first parent.
        This is useful if you are only interested in the topical branch.
        """
        return self._firstParentOnly

    @firstParentOnly.setter
    def firstParentOnly(self, value: bool):
        self._firstParentOnly = value

    @property
    def graph(self):
        return self._graphServer.get_graph()

    @property
    def visitedCommits(self) -> Set[str]:
        """
        Gets a set of visited commits, identified by their their SHA.
        """
        return self._s_visitedCommits

    def compute_commit_scores(self, alpha: float, label_weights: List[float],
                              top_one=False, additive=False):
        """
        Compute the overall scores for all commits by combining DevRank and
        commit classification.
        """
        return commit_overall_scores(self.graph.commit_devranks(alpha),
                                     self._clf_results,
                                     label_weights,
                                     top_one=top_one,
                                     additive=additive)

    async def analyze(self, maxAnalyzedCommits=None, suppressStdOutLogs=False):
        commitSpec = self._terminalCommit
        if self._originCommit:
            commitSpec = self._originCommit.hexsha + ".." + self._terminalCommit.hexsha

        analyzedCommits = 0
        self._graphServer.before_analyze()
        try:
            for commit in self._repo.iter_commits(commitSpec,
                                                  topo_order=True, reverse=True, first_parent=self._firstParentOnly):
                def printCommitStatus(level, status: str):
                    message = commit.message.lstrip()[:32].rstrip()
                    message = re.sub(r"\s+", " ", message)
                    # note the commit # here only indicates the ordinal of current commit in current analysis session
                    if not suppressStdOutLogs:
                        print("Commit #{0} {1} ({2}): {3}".format(
                            analyzedCommits, commit.hexsha, message, status))
                    _logger.log(level, "Commit #%d %s (%s): %s",
                                analyzedCommits, commit.hexsha, message, status)
                lastCommit = self._graphServer.get_workspace_commit_hexsha()
                if maxAnalyzedCommits and analyzedCommits >= maxAnalyzedCommits:
                    _logger.warning("Max analyzed commits reached.")
                    break
                if commit.hexsha in self._visitedCommits:
                    printCommitStatus(logging.DEBUG, "Already visited.")
                    continue
                if len(commit.parents) > 1:
                    # merge commit
                    # process connection, do not process diff
                    printCommitStatus(logging.INFO, "Going forward (merge).")
                    if self._firstParentOnly:
                        assert lastCommit == commit.parents[0].hexsha, \
                            "git should traverse along first parent, but actually not."
                        await self._analyzeCommit(commit, lastCommit, CommitSeekingMode.NormalForward)
                    else:
                        await self._analyzeCommit(commit, lastCommit, CommitSeekingMode.MergeCommit)
                elif not commit.parents:
                    printCommitStatus(
                        logging.INFO, "Going forward (initial commit).")
                    await self._analyzeCommit(commit, None, CommitSeekingMode.NormalForward)
                else:
                    parent: Commit = commit.parents[0]
                    if lastCommit != parent.hexsha:
                        printCommitStatus(
                            logging.INFO, "Rewind to parent: {0}.".format(parent.hexsha))
                        # jumping to the parent commit first
                        await self._analyzeCommit(parent, lastCommit, CommitSeekingMode.Rewind)
                    # then go on with current commit
                    printCommitStatus(logging.INFO, "Going forward.")
                    await self._analyzeCommit(commit, parent, CommitSeekingMode.NormalForward)
                self._visitedCommits.add(commit.hexsha)
                analyzedCommits += 1
        except Exception as ex:
            self._graphServer.after_analyze(ex)
            raise
        else:
            self._graphServer.after_analyze(None)
        return analyzedCommits

    async def _analyzeCommit(self, commit: Union[Commit, str], parentCommit: Union[Commit, str],
                             seekingMode: CommitSeekingMode):
        """
        parentCommit can be None.
        """
        if type(commit) != Commit:
            commit = self._repo.commit(commit)

        t0 = time.monotonic()
        self._observer.onBeforeCommit(self, commit, seekingMode)

        t1 = time.monotonic()
        result = self._graphServer.start_commit(commit.hexsha, seekingMode,
                                                commit.author.name, commit.author.email, commit.message)
        if asyncio.iscoroutine(result):
            await result

        t1 = time.monotonic() - t1
        diff_index = diff_with_commit(self._repo, commit, parentCommit)

        # commit classification
        if self._commit_classifier and commit.hexsha not in self._clf_results:
            prob = self._commit_classifier.predict(commit, diff_index)
            self._clf_results[commit.hexsha] = prob

        t2 = time.monotonic()
        for diff in diff_index:
            old_fname, new_fname = _get_fnames(diff)
            # apply filter
            # if a file comes into/goes from our view, we will set corresponding old_fname/new_fname to None,
            # as if the file is introduced/removed in this commit.
            # However, the diff will keep its original, no matter if the file has been filtered in/out.
            if old_fname and not self._graphServer.filter_file(old_fname):
                old_fname = None
            if new_fname and not self._graphServer.filter_file(new_fname):
                new_fname = None
            if not old_fname and not new_fname:
                # no modification
                continue

            old_src = new_src = None

            if old_fname:
                old_src = get_contents(self._repo, parentCommit, old_fname)

            if new_fname:
                new_src = get_contents(self._repo, commit, new_fname)

            if old_src or new_src:
                result = self._graphServer.update_graph(
                    old_fname, old_src, new_fname, new_src, diff.diff)
                if asyncio.iscoroutine(result):
                    await result
        t2 = time.monotonic() - t2

        t3 = time.monotonic()
        result = self._graphServer.end_commit(commit.hexsha)
        if asyncio.iscoroutine(result):
            await result
        t3 = time.monotonic() - t3
        self._observer.onAfterCommit(self, commit, seekingMode)
        t0 = time.monotonic() - t0
        _logger.info("t0 = %.2f, t1 = %.2f, t2 = %.2f, t3 = %.2f",
                     t0, t1, t2, t3)
        assert self._graphServer.get_workspace_commit_hexsha() == commit.hexsha, \
            "GraphServer.get_workspace_commit_hexsha should be return the hexsha seen in last start_commit."


def _get_fnames(diff: Diff):
    if diff.new_file:
        # change type 'A'
        old_fname = None
        new_fname = diff.b_blob.path
    elif diff.deleted_file:
        # change type 'D'
        old_fname = diff.a_blob.path
        new_fname = None
    elif diff.renamed:
        # change type 'R'
        old_fname = diff.rename_from
        new_fname = diff.rename_to
    elif (diff.a_blob and diff.b_blob and
          (diff.a_blob != diff.b_blob)):
        # change type 'M'
        old_fname = new_fname = diff.b_blob.path
    else:
        # change type 'U'
        return None, None

    return old_fname, new_fname


class AnalyzerObserver(ABC):
    """
    Used to observe the progress of `Analyzer` during its analysis of the target repository.
    You need to derive your own observer class from it before assigning your observer instance
    to `Analyzer.observer`.
    """

    def __init__(self):
        pass

    def onBeforeCommit(self, analyzer: Analyzer, commit: Commit, seeking_mode: CommitSeekingMode):
        """
        Called before the observed Analyzer is about to analyze a commit.
        Params:
            analyzer: the observed Analyzer instance.
            index: the index of the commit, depending on the behavior of the analyzer.
                    This is usually a series of 1-based ordinal index for master commits,
                    and another series of 1-based ordinal index for branch commits.
            commit: the commit to be analyzed.
            isMaster: whether the current commit is one of the master commits.
        """
        pass

    def onAfterCommit(self, analyzer: Analyzer, commit: Commit, seeking_mode: CommitSeekingMode):
        """
        Called after the observed Analyzer has finished analyzing a commit.
        Params:
            analyzer: the observed Analyzer instance.
            index: the index of the commit, depending on the behavior of the analyzer.
                    This is usually a series of 1-based ordinal index for master commits,
                    and another series of 1-based ordinal index for branch commits.
            commit: the commit that has just been analyzed.
            isMaster: whether the current commit is one of the master commits.
        """
        pass


class _EmptyAnalyzerObserverType(AnalyzerObserver):
    pass


emptyAnalyzerObserver = _EmptyAnalyzerObserverType()
"""
An AnalyzerObserver instance that does nothing in their notification methods.
"""


class _ReadOnlySet(collections.abc.Set):
    def __init__(self, underlyingSet: collections.abc.Set):
        self._underlyingSet = underlyingSet

    def __contains__(self, x):
        return x in self._underlyingSet

    def __len__(self):
        return len(self._underlyingSet)

    def __iter__(self):
        return self._underlyingSet.__iter__()
