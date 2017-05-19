import networkx as nx
from graphs.processor import Processor
from graphs.patch_parser import PatchParser
from graphs.srcml import transform_src_to_tree
from graphs.detect_change import get_changed_functions
from graphs.call_graph.c import update_call_graph, get_func_ranges_c
from graphs.devrank import devrank
from graphs.git import get_contents

class CallCommitGraph(Processor):

    def __init__(self, repo_path):
        super().__init__(repo_path)
        self.commits = None
        self.G = None
        self.exts = ('.c', )
        self.history = {}
        self.share = {}
        self.patch_parser = PatchParser()

    def start_process(self):
        self.G = nx.DiGraph()
        self.history = {}

    def start_process_commit(self, commit):
        self.history[commit.hexsha] = {}

    def on_add(self, diff, commit):
        old_fname = None
        new_fname = diff.b_blob.path
        return self._process_helper(diff, commit, old_fname, new_fname)

    def on_delete(self, diff, commit):
        old_fname = diff.a_blob.path
        new_fname = None
        return self._process_helper(diff, commit, old_fname, new_fname)

    def on_rename(self, diff, commit):
        new_fname = diff.rename_to
        old_fname = diff.rename_from
        return self._process_helper(diff, commit, old_fname, new_fname)

    def on_modify(self, diff, commit):
        fname = diff.b_blob.path
        return self._process_helper(diff, commit, fname, fname)

    def fname_filter(self, fname):
        for ext in self.exts:
            if not fname.endswith(ext):
                return False
        return True

    def _get_xml_root(self, commit, fname):
        return transform_src_to_tree(get_contents(self.repo, commit, fname))

    def _process_helper(self, diff, commit, 
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
            if old_fname != None:
                additions, deletions = self.parse_patch(diff.diff)
                if additions == None or deletions == None:
                    return -1

                old_root = self._get_xml_root(commit.parents[0], old_fname)
                if old_root == None:
                    return -1

                modified_func = get_changed_functions(
                    *get_func_ranges_c(old_root), additions, deletions)
                
            # parse new src to tree
            if new_fname != None:
                new_root = self._get_xml_root(commit, new_fname)
                if new_root == None:
                    return -1 
                update_roots.append(new_root)

            # update call graph
            # if on delete, then new_func is expected to be an empty dict
            new_func = update_call_graph(self.G, update_roots, modified_func) 

            # update self.history
            for func_name in new_func:
                self.history[commit.hexsha][func_name] = new_func[func_name] 

            for func_name in modified_func:
                self.history[commit.hexsha][func_name] = modified_func[func_name]

        return 0

    def parse_patch(self, patch):
        additions, deletions = None, None
        try:
            additions, deletions = self.patch_parser.parse(
                patch.decode("utf-8"))
        except UnicodeDecodeError:
            print("UnicodeDecodeError in function parse_patch!")
        except:
            pdb.set_trace()
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
    
    def locrank_commits(self):
        self.loc = {}
        for sha in self.history:
            self.loc[sha] = 0
            for func_name in self.history[sha]:
                self.loc[sha] += self.history[sha][func_name]
        return sorted(self.loc.items(), key=lambda x: x[1], reverse=True)

