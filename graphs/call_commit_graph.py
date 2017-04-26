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
        fname = diff.b_blob.path
        if self.fname_filter(fname):
            file_contents = get_contents(self.repo, commit, fname)
            root = transform_src_to_tree(file_contents)
            if root == None:
                return -1 

            # update call graph
            new_func = update_call_graph(self.G, [root], {}) 

            # update self.history
            for func_name in new_func:
                self.history[commit.hexsha][func_name] = new_func[func_name]

        return 0 

    def on_delete(self, diff, commit):
        fname = diff.a_blob.path
        if self.fname_filter(fname):

            # parse patch
            additions, deletions = self.parse_patch(diff.diff)
            if additions == None or deletions == None:
                return -1
            else:
                assert(len(additions) == 0)
                
            # detect which functions are changed
            last_commit = commit.parents[0]
            file_contents = get_contents(self.repo, last_commit, fname)
            root = transform_src_to_tree(file_contents)
            if root == None:
                return -1
            func_names, func_ranges = get_func_ranges_c(root)

            modified_func = get_changed_functions(func_names, func_ranges, 
                additions, deletions)

            # update call graph
            update_call_graph(self.G, [], modified_func)

            # update self.history
            for func_name in modified_func:
                self.history[commit.hexsha][func_name] = modified_func[func_name]
        return 0

    def on_rename(self, diff, commit):
        new_fname = diff.rename_to
        old_fname = diff.rename_from
        if self.fname_filter(new_fname) or self.fname_filter(old_fname):

            # parse patch
            additions, deletions = self.parse_patch(diff.diff)
            if additions == None or deletions == None:
                return -1
                
            # parse new contents to tree
            new_contents = get_contents(self.repo, commit, new_fname)
            new_root = transform_src_to_tree(new_contents)
            if new_root == None:
                return -1 

            # detect which functions are changed
            last_commit = commit.parents[0]
            old_contents = get_contents(self.repo, last_commit, old_fname)
            old_root = transform_src_to_tree(old_contents)
            if old_root == None:
                return -1 
            func_names, func_ranges = get_func_ranges_c(old_root)

            modified_func = get_changed_functions(func_names, func_ranges, 
                additions, deletions)

            # update call graph
            new_func = update_call_graph(self.G, [new_root], modified_func) 

            # update self.history
            for func_name in new_func:
                self.history[commit.hexsha][func_name] = new_func[func_name] 

            for func_name in modified_func:
                self.history[commit.hexsha][func_name] = modified_func[func_name]

        return 0

    def on_modify(self, diff, commit):
        fname = diff.b_blob.path
        if self.fname_filter(fname):

            # parse patch
            additions, deletions = self.parse_patch(diff.diff)
            if additions == None or deletions == None:
                return -1 

            # parse new contents to tree
            new_contents = get_contents(self.repo, commit, fname)
            new_root = transform_src_to_tree(new_contents)
            if new_root == None:
                return -1 

            # detect which functions are changed
            last_commit = commit.parents[0]
            old_contents = get_contents(self.repo, last_commit, fname)
            old_root = transform_src_to_tree(old_contents)
            if old_root == None:
                return -1 
            func_names, func_ranges = get_func_ranges_c(old_root)

            modified_func = get_changed_functions(func_names, func_ranges, additions, deletions)
                
            # update call graph
            new_func = update_call_graph(self.G, [new_root], modified_func)

            # update self.history
            for func_name in new_func:
                self.history[commit.hexsha][func_name] = new_func[func_name] 

            for func_name in modified_func:
                self.history[commit.hexsha][func_name] = modified_func[func_name]

        return 0

    def fname_filter(self, fname):
        for ext in self.exts:
            if not fname.endswith(ext):
                return False
        return True

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

