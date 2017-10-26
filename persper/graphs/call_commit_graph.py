import sys
import networkx as nx
from persper.graphs.processor import Processor, _diff_with_first_parent, _fill_change_type
from persper.graphs.patch_parser import PatchParser
from persper.graphs.srcml import transform_src_to_tree
from persper.graphs.detect_change import get_changed_functions
from persper.graphs.call_graph.c import update_call_graph_c, get_func_ranges_c
from persper.graphs.call_graph.java import update_call_graph_java, get_func_ranges_java
from persper.graphs.call_graph.java import prepare_env
from persper.graphs.devrank import devrank
from persper.graphs.git_tools import get_contents


def _inverse_diff_result(adds, dels):
    """
    >>> adds = [[11, 1], [32, 1]]
    >>> dels = [[11, 11], [31, 32]]
    >>> _inverse_diff_result(adds, dels)
    ([[10, 1], [30, 2]], [[11, 11], [31, 31]])
    """
    diff = 0
    add_ptr, del_ptr = 0, 0
    num_adds, num_dels = len(adds), len(dels)
    inv_adds, inv_dels = [], []

    def _handle_a(a):
        nonlocal diff
        inv_dels.append([diff + a[0] + 1, diff + a[0] + a[1]])
        diff += a[1]

    def _handle_d(d):
        nonlocal diff
        inv_adds.append([diff + d[0] - 1, d[1] - d[0] + 1])
        diff -= (d[1] - d[0] + 1)

    while add_ptr < num_adds or del_ptr < num_dels:
        if add_ptr < num_adds and del_ptr < num_dels:
            if adds[add_ptr][0] < dels[del_ptr][0]:
                _handle_a(adds[add_ptr])
                add_ptr += 1
            else:
                _handle_d(dels[del_ptr])
                del_ptr += 1
        elif add_ptr < num_adds and del_ptr >= num_dels:
            # we have finished dels
            _handle_a(adds[add_ptr])
            add_ptr += 1
        else:
            # we have finished adds
            _handle_d(dels[del_ptr])
            del_ptr += 1

    return inv_adds, inv_dels


def _normalize_shares(email_to_share):
    share_sum = 0
    for email, share in email_to_share.items():
        share_sum += share

    for email in email_to_share:
        email_to_share[email] /= share_sum


class CallCommitGraph(Processor):

    def __init__(self, repo_path, lang='c'):
        super().__init__(repo_path)
        self.G = None
        self.lang = lang
        if lang == 'c':
            self.exts = ('.c', '.h')
        elif lang == 'java':
            self.exts = ('.java',)
        else:
            print("Invalid language option, terminated.")
            sys.exit(-1)
        self.env = {}
        self.history = {}
        self.share = {}
        self.patch_parser = PatchParser()

    def _reset_state(self):
        super()._reset_state()
        self.G = nx.DiGraph()
        self.history = {}

    def _start_process_commit(self, commit):
        self.history[commit.hexsha] = {}
        if self.lang == 'java':
            new_roots = []
            diff_index = _diff_with_first_parent(commit)
            _fill_change_type(diff_index)
            for diff in diff_index:
                if diff.change_type in ['A', 'M']:
                    fname = diff.b_blob.path
                elif diff.change_type == 'R':
                    fname = diff.rename_to
                else:
                    continue

                if self.fname_filter(fname):
                    root = self._get_xml_root(commit, fname)
                    prepare_env(root, env=self.env)

    def on_add(self, diff, commit, is_merge_commit):
        old_fname = None
        new_fname = diff.b_blob.path
        return self._first_phase(diff, commit,
                                 is_merge_commit,
                                 old_fname=old_fname,
                                 new_fname=new_fname)

    def on_delete(self, diff, commit, is_merge_commit):
        old_fname = diff.a_blob.path
        new_fname = None
        return self._first_phase(diff, commit,
                                 is_merge_commit,
                                 old_fname=old_fname,
                                 new_fname=new_fname)

    def on_rename(self, diff, commit, is_merge_commit):
        new_fname = diff.rename_to
        old_fname = diff.rename_from
        return self._first_phase(diff, commit,
                                 is_merge_commit,
                                 old_fname=old_fname,
                                 new_fname=new_fname)

    def on_modify(self, diff, commit, is_merge_commit):
        fname = diff.b_blob.path
        return self._first_phase(diff, commit,
                                 is_merge_commit,
                                 old_fname=fname,
                                 new_fname=fname)

    def on_add2(self, diff, commit):
        old_fname = None
        new_fname = diff.b_blob.path
        return self._second_phase(diff, commit,
                                  old_fname=old_fname,
                                  new_fname=new_fname)

    def on_delete2(self, diff, commit):
        old_fname = diff.a_blob.path
        new_fname = None
        return self._second_phase(diff, commit,
                                  old_fname=old_fname,
                                  new_fname=new_fname)

    def on_rename2(self, diff, commit):
        new_fname = diff.rename_to
        old_fname = diff.rename_from
        return self._second_phase(diff, commit,
                                  old_fname=old_fname,
                                  new_fname=new_fname)

    def on_modify2(self, diff, commit):
        fname = diff.b_blob.path
        return self._second_phase(diff, commit,
                                  old_fname=fname,
                                  new_fname=fname)

    def fname_filter(self, fname):
        for ext in self.exts:
            if fname.endswith(ext):
                return True
        return False

    def _get_xml_root(self, commit, fname):
        if self.lang == 'c':
            return transform_src_to_tree(
                get_contents(self.repo, commit, fname))
        elif self.lang == 'java':
            return transform_src_to_tree(
                get_contents(self.repo, commit, fname), ext='.java')

    def _first_phase(self, diff, commit, is_merge_commit,
                     old_fname=None, new_fname=None):

        if ((old_fname and self.fname_filter(old_fname)) or
           (new_fname and self.fname_filter(new_fname))):

            # on add, rename, modify: update_roots = [new_root]
            # on delete: update_roots = []
            update_roots = []

            # on add: modified_func = {}
            # on rename, modify, delete: modified_func is computed by
            #   parsing patch and call get_changed_functions
            modified_func = {}

            # do not need to parse patch if on add
            if old_fname is not None:
                additions, deletions = self.parse_patch(diff.diff)
                if additions is None or deletions is None:
                    return -1

                old_root = self._get_xml_root(commit.parents[0], old_fname)
                if old_root is None:
                    return -1

                if self.lang == 'c':
                    modified_func = get_changed_functions(
                        *get_func_ranges_c(old_root), additions, deletions)
                elif self.lang == 'java':
                    modified_func = get_changed_functions(
                        *get_func_ranges_java(old_root), additions, deletions)

            # parse new src to tree
            if new_fname is not None:
                new_root = self._get_xml_root(commit, new_fname)
                if new_root is None:
                    return -1
                update_roots.append(new_root)

            # update call graph
            # if on delete, then new_func is expected to be an empty dict
            if self.lang == 'c':
                new_func = update_call_graph_c(
                    self.G, update_roots, modified_func)
            elif self.lang == 'java':
                new_func = update_call_graph_java(
                    self.G, update_roots, modified_func, env=self.env)

            # only update self.history for non-merge commit
            if not is_merge_commit:
                for func_name in new_func:
                    self.history[commit.hexsha][func_name] = \
                        new_func[func_name]

                for func_name in modified_func:
                    self.history[commit.hexsha][func_name] = \
                        modified_func[func_name]

        return 0

    def _second_phase(self, diff, commit, old_fname=None, new_fname=None):

        if ((old_fname and self.fname_filter(old_fname)) or
           (new_fname and self.fname_filter(new_fname))):

            adds, dels = self.parse_patch(diff.diff)
            if adds is None or dels is None:
                return -1
            modified_func, inv_modified_func = {}, {}

            if old_fname is not None:
                old_root = self._get_xml_root(commit.parents[0], old_fname)
                if old_root is None:
                    return -1

                if self.lang == 'c':
                    modified_func = get_changed_functions(
                        *get_func_ranges_c(old_root), adds, dels)
                elif self.lang == 'java':
                    modified_func = get_changed_functions(
                        *get_func_ranges_java(old_root), adds, dels)

            if new_fname is not None:
                inv_adds, inv_dels = _inverse_diff_result(adds, dels)
                new_root = self._get_xml_root(commit, new_fname)
                if new_root is None:
                    return -1

                if self.lang == 'c':
                    inv_modified_func = get_changed_functions(
                        *get_func_ranges_c(new_root), inv_adds, inv_dels)
                elif self.lang == 'java':
                    inv_modified_func = get_changed_functions(
                        *get_func_ranges_java(new_root), inv_adds, inv_dels)

            for func_name in modified_func:
                if func_name in self.G:
                    self.history[commit.hexsha][func_name] = \
                        modified_func[func_name]

            for func_name in inv_modified_func:
                if func_name in self.G and func_name not in modified_func:
                    self.history[commit.hexsha][func_name] = \
                       inv_modified_func[func_name]

    def parse_patch(self, patch):
        additions, deletions = None, None
        try:
            additions, deletions = self.patch_parser.parse(
                patch.decode('utf-8', 'replace'))
        except UnicodeDecodeError:
            print("UnicodeDecodeError in function parse_patch!")
        except:
            print("Unknown error in function parse_patch!")
        return additions, deletions

    def update_shares(self, alpha):
        self.scores = devrank(self.G, alpha=alpha)
        for sha in self.history:
            self.share[sha] = 0
            for func_name in self.history[sha]:
                if func_name in self.G:
                    # this condition handles the case where
                    # func_name is deleted by sha,
                    # but has never been added or modified before
                    self.share[sha] += \
                        (self.history[sha][func_name] /
                            self.G.node[func_name]['num_lines']) \
                        * self.scores[func_name]

    def devrank_commits(self, alpha):
        self.update_shares(alpha)
        return sorted(self.share.items(), key=lambda x: x[1], reverse=True)

    def devrank_functions(self, alpha):
        self.scores = devrank(self.G, alpha=alpha)
        return sorted(self.scores.items(), key=lambda x: x[1], reverse=True)

    def devrank_developers(self, alpha, sha_to_type={}, coefs=[1, 1, 1, 1]):
        self.update_shares(alpha)
        email_to_share = {}
        email_to_name = {}

        hexsha_to_type = {}
        for sha, t in sha_to_type.items():
            c = self.repo.commit(sha)
            hexsha_to_type[c.hexsha] = t

        for sha in self.history:
            if sha in hexsha_to_type:
                coef = coefs[int(hexsha_to_type[sha])]
            else:
                coef = 1
            actor = self.repo.commit(sha).author
            email = actor.email
            email_to_name[email] = actor.name
            if email in email_to_share:
                email_to_share[email] += coef * self.share[sha]
            else:
                email_to_share[email] = coef * self.share[sha]
        _normalize_shares(email_to_share)
        sorted_shares = sorted(email_to_share.items(),
                               key=lambda x: x[1],
                               reverse=True)
        return sorted_shares, email_to_name

    def locrank_commits(self):
        self.loc = {}
        for sha in self.history:
            self.loc[sha] = 0
            for func_name in self.history[sha]:
                self.loc[sha] += self.history[sha][func_name]
        return sorted(self.loc.items(), key=lambda x: x[1], reverse=True)

    def __getstate__(self):
        state = super().__getstate__()
        state['G'] = self.G
        state['history'] = self.history
        state['lang'] = self.lang
        state['exts'] = self.exts
        state['env'] = self.env
        return state

    def __setstate__(self, state):
        super().__setstate__(state)
        self.share = {}
        self.patch_parser = PatchParser()

if __name__ == "__main__":
    import doctest
    doctest.testmod()
