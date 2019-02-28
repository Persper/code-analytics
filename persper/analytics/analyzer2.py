import asyncio
from abc import ABC
import collections.abc
from typing import Union, Set

from git import Commit, Diff, DiffIndex, Repo

from persper.analytics.git_tools import (EMPTY_TREE_SHA, diff_with_commit,
                                         get_contents)
from persper.analytics.graph_server import CommitSeekingMode, GraphServer


class Analyzer:
    def __init__(self, repositoryRoot: str, graphServer: GraphServer,
                 terminalCommit: str = "master",
                 firstParentOnly: bool = False):
        self._repositoryRoot = repositoryRoot
        self._graphServer = graphServer
        self._repo = Repo(repositoryRoot)
        self._originCommit: Commit = None
        self._terminalCommit: Commit = self._repo.rev_parse(terminalCommit)
        self._firstParentOnly = firstParentOnly
        self._visitedCommits = set()
        self._s_visitedCommits = _ReadOnlySet(self._visitedCommits)
        self._observer: AnalyzerObserver = emptyAnalyzerObserver

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
        self._originCommit = self._repo.rev_parse(value) if value else None

    @property
    def terminalCommit(self):
        """
        Gets/sets the last commit to visit. (inclusive)
        """
        return self._terminalCommit

    @terminalCommit.setter
    def terminalCommit(self, value: Union[Commit, str]):
        self._terminalCommit = self._repo.rev_parse(value)

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

    async def analyze(self, maxAnalyzedCommits=1000):
        graphServerLastCommit = EMPTY_TREE_SHA
        commitSpec = self._terminalCommit
        if self._originCommit:
            commitSpec = self._originCommit.hexsha + ".." + self._terminalCommit.hexsha
        analyzedCommits = 0
        for commit in self._repo.iter_commits(commitSpec,
                                              topo_order=True, reverse=True, first_parent=self._firstParentOnly):
            def printCommitStatus(status: str):
                message = commit.message.strip()[:32]
                # note the commit # here only indicates the ordinal of current commit in current analysis session
                print("Commit #{0} {1} ({2}): {3}".format(analyzedCommits, commit.hexsha, message, status))

            if maxAnalyzedCommits and analyzedCommits >= maxAnalyzedCommits:
                print("Max analyzed commits reached.")
                break
            if commit.hexsha in self._visitedCommits:
                printCommitStatus("Already visited.")
                continue
            if len(commit.parents) > 1:
                # merge commit
                # process connection, do not process diff
                printCommitStatus("Going forward (merge).")
                if self._firstParentOnly:
                    assert graphServerLastCommit == commit.parents[0].hexsha, \
                        "git should traverse along first parent, but actually not."
                    await self._analyzeCommit(commit, graphServerLastCommit, CommitSeekingMode.NormalForward)
                else:
                    await self._analyzeCommit(commit, graphServerLastCommit, CommitSeekingMode.MergeCommit)
            elif not commit.parents:
                printCommitStatus("Going forward (initial commit).")
                await self._analyzeCommit(commit, None, CommitSeekingMode.NormalForward)
            else:
                parent: Commit = commit.parents[0]
                if graphServerLastCommit != parent.hexsha:
                    printCommitStatus(
                        "Rewind to parent: {0}.".format(parent.hexsha))
                    # jumping to the parent commit first
                    await self._analyzeCommit(parent, graphServerLastCommit, CommitSeekingMode.Rewind)
                # then go on with current commit
                printCommitStatus("Going forward.")
                await self._analyzeCommit(commit, parent, CommitSeekingMode.NormalForward)
            graphServerLastCommit = commit.hexsha
            analyzedCommits += 1

    async def _analyzeCommit(self, commit: Union[Commit, str], parentCommit: Union[Commit, str],
                             seekingMode: CommitSeekingMode):
        """
        parentCommit can be None.
        """
        if type(commit) != Commit:
            commit = self._repo.commit(commit)
        self._observer.onBeforeCommit(self, commit, seekingMode)
        result = self._graphServer.start_commit(commit.hexsha, seekingMode,
                                                commit.author.name, commit.author.email, commit.message)
        if asyncio.iscoroutine(result):
            await result
        diff_index = diff_with_commit(self._repo, commit, parentCommit)

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

        result = self._graphServer.end_commit(commit.hexsha)
        if asyncio.iscoroutine(result):
            await result
        self._observer.onAfterCommit(self, commit, seekingMode)


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
