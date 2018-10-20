import re
import networkx as nx
from persper.graphs.patch_parser import PatchParser
from persper.graphs.srcml import transform_src_to_tree
from persper.graphs.call_graph.c import update_call_graph_c, get_func_ranges_c
from persper.graphs.detect_change import get_changed_functions
from persper.graphs.inverse_diff import inverse_diff
from persper.graphs.graph_server import GraphServer


class CGraphServer(GraphServer):
    def __init__(self, filename_regex_strs):
        self._graph = nx.DiGraph()
        self._filename_regexes = [re.compile(regex_str) for regex_str in filename_regex_strs]
        self._pparser = PatchParser()

    def update_graph(self, old_filename, old_src, new_filename, new_src, patch):
        # on add, rename, modify: update_roots = [new_root]
        # on delete: update_roots = []
        update_root = []

        # on add: modified_func = {}
        # on rename, modify, delete: modified_func is computed by
        #   parsing patch and call get_changed_functions
        modified_func = {}

        if old_src is not None:
            old_root = transform_src_to_tree(old_src)
            if old_root is None:
                return {}, {}

            modified_func = get_changed_functions(
                *get_func_ranges_c(old_root),
                *self._parse_patch(patch))

        if new_src is not None:
            new_root = transform_src_to_tree(new_src)
            if new_root is None:
                return {}, {}
            update_root = [new_root]

        # update call graph
        # if on delete, then new_func is expected to be an empty dict
        new_func = update_call_graph_c(self.graph, update_root, modified_func)

        # return history
        return {**new_func, **modified_func}, {}

    def parse(self, old_filename, old_src, new_filename, new_src, patch):
        """Return None if there is an error"""
        forward_stats = {}
        bckward_stats = {}

        adds, dels = self._parse_patch(patch)
        if adds is None or dels is None:
            return None, {}

        if old_src is not None:
            old_root = transform_src_to_tree(old_src)
            if old_root is None:
                return None, {}

            forward_stats = get_changed_functions(
                *get_func_ranges_c(old_root), adds, dels)

        if new_src is not None:
            inv_adds, inv_dels = inverse_diff(adds, dels)
            new_root = transform_src_to_tree(new_src)
            if new_root is None:
                return None, {}

            bckward_stats = get_changed_functions(
                *get_func_ranges_c(new_root), inv_adds, inv_dels)

        """
        forward_stats and bckward_stats might have different values
        for the same function, as an example, please refer to
        `str_equals` function in the following link. In this case,
        we'll stick with forward_stats (override bckward_stats).
        https://github.com/UltimateBeaver/test_feature_branch/commit/364d5cc49aeb2e354da458924ce84c0ab731ac77
        """
        bckward_stats.update(forward_stats)
        return bckward_stats, {}

    def get_graph(self):
        return self.graph

    def reset_graph(self):
        self.graph = nx.DiGraph()

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
