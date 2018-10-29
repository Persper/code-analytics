import re
from persper.analytics.inverse_diff import inverse_diff
from persper.analytics.srcml import transform_src_to_tree
from persper.analytics.call_graph.c import update_graph, get_func_ranges_c
from persper.analytics.detect_change import get_changed_functions
from persper.analytics.patch_parser import PatchParser
from persper.analytics.graph_server import GraphServer
from persper.analytics.call_commit_graph import CallCommitGraph


class CGraphServer(GraphServer):
    def __init__(self, filename_regex_strs):
        self._ccgraph = CallCommitGraph()
        self._filename_regexes = [re.compile(regex_str) for regex_str in filename_regex_strs]
        self._pparser = PatchParser()

    def register_commit(self, hexsha, author_name, author_email,
                        commit_message):
        self._ccgraph.add_commit(hexsha, author_name, author_email,
                                 commit_message)

    def update_graph(self, old_filename, old_src, new_filename, new_src, patch):
        ast_list = []
        forward_stats = {}
        bckward_stats = {}
        adds, dels = self._parse_patch(patch)

        if old_src:
            old_ast = transform_src_to_tree(old_src)
            if old_ast is None:
                return -1

            forward_stats = get_changed_functions(
                *get_func_ranges_c(old_ast), adds, dels)

        if new_src:
            new_ast = transform_src_to_tree(new_src)
            if new_ast is None:
                return -1

            ast_list = [new_ast]
            inv_adds, inv_dels = inverse_diff(adds, dels)
            bckward_stats = get_changed_functions(
                *get_func_ranges_c(new_ast), inv_adds, inv_dels)

        bckward_stats.update(forward_stats)
        update_graph(self._ccgraph, ast_list, bckward_stats)
        return 0

    def get_graph(self):
        return self._ccgraph

    def reset_graph(self):
        self._ccgraph.reset()

    def filter_file(self, filename):
        for regex in self._filename_regexes:
            if not regex.match(filename):
                return False
        return True

    def config(self, param):
        pass

    def _parse_patch(self, patch):
        adds, dels = None, None
        try:
            adds, dels = self._pparser.parse(patch.decode('utf-8', 'replace'))
        except UnicodeDecodeError:
            print("UnicodeDecodeError when parsing patch!")
        except:
            print("Unknown error when parsing patch!")
        return adds, dels
