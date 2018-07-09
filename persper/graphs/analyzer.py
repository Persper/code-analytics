import os
import time
import pickle
from persper.graphs.devrank import devrank
from persper.graphs.git_tools import get_contents, _diff_with_first_parent
from persper.graphs.iterator import RepoIterator
from persper.util.bidict import bidict


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


def _normalize_shares(email_to_share):
    share_sum = 0
    for email, share in email_to_share.items():
        share_sum += share

    for email in email_to_share:
        email_to_share[email] /= share_sum


class Analyzer():

    def __init__(self, repo_path, ccg):
        self.ccg = ccg
        self.ri = RepoIterator(repo_path)
        self.history = {}
        self.id_map = {}
        self.ordered_shas = []

    def analyze(self, rev=None,
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
            self.ccg.reset_graph()

        commits, branch_commits = \
            self.ri.iter(rev=rev,
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
            self.analyze_master_commit(commit)
            self.autosave(phase, idx, checkpoint_interval)

        for idx, commit in enumerate(branch_commits, 1):
            phase = 'branch'
            print_commit_info(phase, idx, commit, start_time, verbose)
            self.analyze_branch_commit(commit)
            self.autosave(phase, idx, checkpoint_interval)

        self.autosave('finished', 0, 1)

    def _analyze_commit(self, commit, ccg_func):
        sha = commit.hexsha
        self.ordered_shas.append(sha)
        self.history[sha] = {}
        self.id_map[sha] = {}
        diff_index = _diff_with_first_parent(commit)

        for diff in diff_index:
            old_fname, new_fname = _get_fnames(diff)
            # Cases we don't handle
            # 1. Both file names are None
            if old_fname is None and new_fname is None:
                print('WARNING: unknown change type encountered.')
                continue

            # 2. Either old_fname and new_fname doesn't pass filter
            if ((old_fname and not self.ccg.fname_filter(old_fname)) or
               (new_fname and not self.ccg.fname_filter(new_fname))):
                continue

            old_src = new_src = None

            if old_fname:
                old_src = get_contents(
                    self.ri.repo, commit.parents[0], old_fname)

            if new_fname:
                new_src = get_contents(self.ri.repo, commit, new_fname)

            if old_src or new_src:
                # Delegate actual work to ccg
                id_to_lines, id_map = ccg_func(
                    old_fname, old_src, new_fname, new_src, diff.diff)

                self.history[sha].update(id_to_lines)
                self.id_map[sha].update(id_map)

    def analyze_master_commit(self, commit):
        self._analyze_commit(commit, self.ccg.update_graph)

    def analyze_branch_commit(self, commit):
        self._analyze_commit(commit, self.ccg.get_change_stats)

    def reset_state(self):
        self.history = {}
        self.id_map = {}
        self.ordered_shas = []
        self.G = None

    def build_history(self,
                      commits,
                      phase='build-history',
                      checkpoint_interval=1000,
                      verbose=False):
        """A helper function to access `analyze_branch_commit`"""
        print_overview([], commits)
        start_time = time.time()

        for idx, commit in enumerate(commits, 1):
            print_commit_info(phase, idx, commit, start_time, verbose)
            self.analyze_branch_commit(commit)
            self.autosave(phase, idx, checkpoint_interval)

        self.autosave(phase, 0, 1)

    def aggregate_id_map(self):
        final_map = bidict()
        for sha in self.ordered_shas:
            for old_fid, new_fid in self.id_map[sha].items():
                if old_fid in final_map.inverse:
                    # Make a copy so that we don't remove list elements
                    # during iteration
                    existing_fids = final_map.inverse[old_fid].copy()
                    for ex_fid in existing_fids:
                        final_map[ex_fid] = new_fid
                final_map[old_fid] = new_fid
        return dict(final_map)

    def cache_graph(self):
        self.G = self.ccg.get_graph()

    def compute_function_share(self, alpha):
        self.cache_graph()
        return devrank(self.G, alpha=alpha)

    def compute_commit_share(self, alpha):
        commit_share = {}
        func_share = self.compute_function_share(alpha)
        final_map = self.aggregate_id_map()

        # Compute final history using final_map
        final_history = {}
        for sha in self.history:
            final_history[sha] = {}
            for fid, num_lines in self.history[sha].items():
                if fid in final_map:
                    final_history[sha][final_map[fid]] = num_lines
                else:
                    final_history[sha][fid] = num_lines

        # Propagate to commit level
        for sha in final_history:
            commit_share[sha] = 0
            for fid in final_history[sha]:
                if fid in self.G:
                    """
                    this condition handles the case where
                    func is deleted by sha,
                    but has never been added or modified before
                    """
                    commit_share[sha] += \
                        (final_history[sha][fid] /
                         self.G.node[fid]['num_lines'] *
                         func_share[fid])

        return commit_share

    def locrank_commits(self):
        loc = {}
        for sha in self.history:
            loc[sha] = 0
            for func in self.history[sha]:
                loc[sha] += self.history[sha][func]
        return sorted(loc.items(), key=lambda x: x[1], reverse=True)

    def save(self, fname):
        with open(fname, 'wb+') as f:
            pickle.dump(self, f)

    def autosave(self, phase, idx, checkpoint_interval):
        if idx % checkpoint_interval == 0:
            repo_name = os.path.basename(self.ri.repo_path.rstrip('/'))
            fname = repo_name + '-' + phase + '-' + str(idx) + '.pickle'
            self.save(fname)
