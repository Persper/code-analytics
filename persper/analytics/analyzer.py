import os
import time
import pickle
import asyncio
from persper.analytics.git_tools import get_contents, diff_with_first_parent, initialize_repo
from persper.analytics.iterator import RepoIterator
from abc import ABC
from git import Commit


def print_overview(commits, branch_commits):
    print('----- Overview ------')
    print('# of commits on master: %d' % len(commits))
    print('# of commits on branch: %d' % len(branch_commits))


def print_commit_info(phase, idx, commit, start_time, verbose):
    if verbose:
        print('----- No.%d %s %s %s -----' %
              (idx, commit.hexsha, subject_of(commit.message),
               time.strftime("%b %d %Y", time.gmtime(commit.authored_date))))
    else:
        print('----- No.%d %s on %s -----' % (idx, commit.hexsha, phase))

    if idx % 100 == 0:
        print('------ Used time: %.3f -----' % (time.time() - start_time))


def subject_of(msg):
    return msg.split('\n', 1)[0].lstrip().rstrip()


def _get_fnames(diff):
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


def is_merge_commit(commit):
    return len(commit.parents) > 1


class Analyzer:

    def __init__(self, repo_path, graph_server):
        self._graph_server = graph_server
        self._repo_path = repo_path
        self._ri = RepoIterator(repo_path)
        self._repo = initialize_repo(repo_path)
        self._ccgraph = None
        self._observer: AnalyzerObserver = emptyAnalyzerObserver

    @property
    def observer(self):
        """
        The AnalyzerObserver used to observe current Analyzer.
        """
        return self._observer

    @observer.setter
    def observer(self, value):
        self._observer = value or emptyAnalyzerObserver

    async def analyze(self, rev=None,
                from_beginning=False,
                num_commits=None,
                continue_iter=False,
                end_commit_sha=None,
                into_branches=False,
                max_branch_length=100,
                min_branch_date=None,
                checkpoint_interval=1000,
                verbose=False):

        if not continue_iter:
            self.reset_state()
            self._graph_server.reset_graph()

        commits, branch_commits = \
            self._ri.iter(rev=rev,
                          from_beginning=from_beginning,
                          num_commits=num_commits,
                          continue_iter=continue_iter,
                          end_commit_sha=end_commit_sha,
                          into_branches=into_branches,
                          max_branch_length=max_branch_length,
                          min_branch_date=min_branch_date)

        print_overview(commits, branch_commits)
        start_time = time.time()

        for idx, commit in enumerate(reversed(commits), 1):
            phase = 'main'
            print_commit_info(phase, idx, commit, start_time, verbose)
            self._observer.onBeforeCommit(self, idx, commit, True)
            await self.analyze_master_commit(commit)
            self._observer.onAfterCommit(self, idx, commit, True)
            self.autosave(phase, idx, checkpoint_interval)

        for idx, commit in enumerate(branch_commits, 1):
            phase = 'branch'
            print_commit_info(phase, idx, commit, start_time, verbose)
            self._observer.onBeforeCommit(self, idx, commit, False)
            await self.analyze_branch_commit(commit)
            self._observer.onAfterCommit(self, idx, commit, False)
            self.autosave(phase, idx, checkpoint_interval)

        self.autosave('finished', 0, 1)

    async def _analyze_commit(self, commit, server_func):
        self._graph_server.register_commit(commit.hexsha,
                                           commit.author.name,
                                           commit.author.email,
                                           commit.message)
        diff_index = diff_with_first_parent(self._repo, commit)

        for diff in diff_index:
            old_fname, new_fname = _get_fnames(diff)
            # Cases we don't handle
            # 1. Both file names are None
            if old_fname is None and new_fname is None:
                print('WARNING: unknown change type encountered.')
                continue

            # 2. Either old_fname and new_fname doesn't pass filter
            if ((old_fname and not self._graph_server.filter_file(old_fname)) or
               (new_fname and not self._graph_server.filter_file(new_fname))):
                continue

            old_src = new_src = None

            if old_fname:
                old_src = get_contents(
                    self._repo, commit.parents[0], old_fname)

            if new_fname:
                new_src = get_contents(self._repo, commit, new_fname)

            if old_src or new_src:
                # todo (hezheng) store the status somewhere for reporting later
                result = server_func(old_fname, old_src, new_fname, new_src, diff.diff)
                if asyncio.iscoroutine(result):
                    result = await result
                status = result

        result = self._graph_server.end_commit(commit.hexsha)
        if asyncio.iscoroutine(result):
            result = await result

    async def analyze_master_commit(self, commit):
        await self._analyze_commit(commit, self._graph_server.update_graph)

    # todo (hezheng) implement correct analysis for branches
    async def analyze_branch_commit(self, commit):
        await self._analyze_commit(commit, self._graph_server.update_graph)

    def reset_state(self):
        self._ccgraph = None

    def get_graph(self):
        self._ccgraph = self._graph_server.get_graph()
        return self._ccgraph

    def save(self, fname):
        with open(fname, 'wb+') as f:
            pickle.dump(self, f)

    def autosave(self, phase, idx, checkpoint_interval):
        if idx % checkpoint_interval == 0:
            repo_name = os.path.basename(self._repo_path.rstrip('/'))
            fname = repo_name + '-' + phase + '-' + str(idx) + '.pickle'
            self.save(fname)

    def __getstate__(self):
        state = self.__dict__.copy()
        state.pop("_observer", None)
        return state

    def __setstate__(self, state):
        self.__dict__.update(state)


class AnalyzerObserver(ABC):
    """
    Used to observe the progress of `Analyzer` during its analysis of the target repository.
    You need to derive your own observer class from it before assigning your observer instance
    to `Analyzer.observer`.
    """
    def __init__(self):
        pass

    def onBeforeCommit(self, analyzer:Analyzer, index:int, commit:Commit, isMaster:bool):
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

    def onAfterCommit(self, analyzer:Analyzer, index:int, commit:Commit, isMaster:bool):
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
