from persper.graphs.devrank import devrank
from persper.graphs.git_tools import get_contents, _diff_with_first_parent
from persper.graphs.iterator import RepoIterator


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
        self.share = {}

    def analyze(self, rev=None,
                from_beginning=False,
                num_commits=None,
                continue_iter=False,
                end_commit_sha=None,
                into_branches=False,
                max_branch_length=100,
                min_branch_date=None):

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

        for commit in reversed(commits):
            self.analyze_master_commit(commit, into_branches)

        for commit in branch_commits:
            self.analyze_branch_commit(commit)

    def analyze_master_commit(self, commit, into_branches):
        self.history[commit.hexsha] = {}
        diff_index = _diff_with_first_parent(commit)

        for diff in diff_index:
            old_fname, new_fname = _get_fnames(diff)
            if old_fname is None and new_fname is None:
                print('Unknown change type encountered.')
                continue

            old_src = new_src = None

            if old_fname and self.fname_filter(old_fname):
                old_src = get_contents(
                    self.ri.repo, commit.parents[0], old_fname)

            if new_fname and self.fname_filter(new_fname):
                new_src = get_contents(self.ri.repo, commit, new_fname)

            if old_src or new_src:
                change_stats = self.ccg.update_graph(
                    old_src, new_src, diff.diff)
                if not (into_branches and is_merge_commit(commit)):
                    for func_name, num_lines in change_stats.items():
                        self.history[commit.hexsha][func_name] = num_lines

    def analyze_branch_commit(self, commit):
        self.history[commit.hexsha] = {}
        diff_index = _diff_with_first_parent(commit)

        for diff in diff_index:
            old_fname, new_fname = _get_fnames(diff)
            if old_fname is None and new_fname is None:
                print('Unknown change type encountered.')
                continue

            old_src = new_src = None

            if old_fname and self.fname_filter(old_fname):
                old_src = get_contents(
                    self.ri.repo, commit.parents[0], old_fname)

            if new_fname and self.fname_filter(new_fname):
                new_src = get_contents(self.ri.repo, commit, new_fname)

            if old_src or new_src:
                change_stats = self.ccg.get_change_stats(
                    old_src, new_src, diff.diff)
                # TODO verify correctness
                if not is_merge_commit(commit):
                    for func_name, num_lines in change_stats.items():
                        self.history[commit.hexsha][func_name] = num_lines

    def reset_state(self):
        self.history = {}
        self.share = {}

    def fname_filter(self, fname):
        for ext in self.ccg.exts:
            if fname.endswith(ext):
                return True
        return False

    def compute_shares(self, alpha):
        G = self.ccg.get_graph()
        scores = devrank(G, alpha=alpha)
        for sha in self.history:
            self.share[sha] = 0
            for func in self.history[sha]:
                if func in self.G:
                    """
                    this condition handles the case where
                    func is deleted by sha,
                    but has never been added or modified before
                    """
                    self.share[sha] += \
                        (self.history[sha][func] /
                         self.G.node[func]['num_lines'] *
                         self.scores[func])

    def devrank_commits(self, alpha):
        self.compute_shares(alpha)
        return sorted(self.share.items(), key=lambda x: x[1], reverse=True)

    def devrank_functions(self, alpha):
        G = self.ccg.get_graph()
        scores = devrank(G, alpha=alpha)
        return sorted(scores.items(), key=lambda x: x[1], reverse=True)

    def locrank_commits(self):
        loc = {}
        for sha in self.history:
            loc[sha] = 0
            for func in self.history[sha]:
                loc[sha] += self.history[sha][func]
        return sorted(loc.items(), key=lambda x: x[1], reverse=True)
