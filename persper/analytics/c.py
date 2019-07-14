import re
from typing import List
from persper.analytics.inverse_diff import inverse_diff
from persper.analytics.srcml import src_to_tree
from persper.analytics.call_graph.c import update_graph, get_func_ranges_c
from persper.analytics.detect_change import get_changed_functions
from persper.analytics.patch_parser import PatchParser
from persper.analytics.graph_server import CommitSeekingMode, GraphServer
from persper.analytics.call_commit_graph import CallCommitGraph
from persper.analytics.exclude_patterns import EXCLUDE_PATTERNS


def function_change_stats(old_ast, old_src, new_ast, new_src, patch, patch_parser, ranges_func):
    """
    Parse old/new source files and extract the change info for all functions
    """
    adds, dels = patch_parser(patch)

    forward_stats = {}
    bckward_stats = {}

    if old_ast is not None:
        forward_stats = get_changed_functions(
            *ranges_func(old_ast), adds, dels, old_src, new_src, separate=True)

    if new_ast is not None:
        inv_adds, inv_dels = inverse_diff(adds, dels)
        bckward_stats = get_changed_functions(
            *ranges_func(new_ast), inv_adds, inv_dels, new_src, old_src, separate=True)

    # merge forward and backward stats
    for func, fstat in bckward_stats.items():
        if func not in forward_stats:
            forward_stats[func] = {
                'adds': fstat['dels'],
                'dels': fstat['adds'],
                'added_units': fstat['removed_units'],
                'removed_units': fstat['added_units']
            }

    return forward_stats


class CGraphServer(GraphServer):

    # CGraphServer only analyzes files with the following suffixes
    _suffix_regex = re.compile(r'.+\.(h|c)$')

    def __init__(self, exclude_patterns: List[str] = EXCLUDE_PATTERNS):
        super(CGraphServer, self).__init__(exclude_patterns=exclude_patterns)
        self._ccgraph = CallCommitGraph()
        self._pparser = PatchParser()
        self._seeking_mode = None
        self._workspace_commit_hexsha = None

    def start_commit(self, hexsha: str, seeking_mode: CommitSeekingMode,
                     author_name: str, author_email: str, commit_message: str):
        self._seeking_mode = seeking_mode
        self._ccgraph.add_commit(hexsha, author_name, author_email,
                                 commit_message)
        self._workspace_commit_hexsha = hexsha

    def register_commit(self, hexsha, author_name, author_email,
                        commit_message):
        self._ccgraph.add_commit(hexsha, author_name, author_email,
                                 commit_message)

    def get_workspace_commit_hexsha(self):
        return self._workspace_commit_hexsha

    def update_graph(self, old_filename, old_src, new_filename, new_src, patch, cache=None):
        ast_list = []
        old_ast = None
        new_ast = None

        # Do nothing if in rewind mode
        if self._seeking_mode == CommitSeekingMode.Rewind:
            return 0

        # Parse source codes into ASTs
        if old_src:
            old_ast = self._get_ast(old_filename, old_src, cache)
            if old_ast is None:
                return -1

        if new_src:
            new_ast = self._get_ast(new_filename, new_src, cache)
            if new_ast is None:
                return -1
            ast_list = [new_ast]

        # Compute function change stats
        # Compatible with both the old and the new Analyzer
        change_stats = {}
        if self._seeking_mode != CommitSeekingMode.MergeCommit:
            change_stats = function_change_stats(old_ast, old_src, new_ast, new_src, patch,
                                                 self._parse_patch,
                                                 get_func_ranges_c)

        # Update call-commit graph
        new_fname_to_old_fname = {}
        if old_filename is not None and new_filename is not None and \
           old_filename != new_filename:
            new_fname_to_old_fname = {new_filename: old_filename}
        update_graph(self._ccgraph, ast_list, change_stats, new_fname_to_old_fname)
        return 0

    def get_graph(self):
        return self._ccgraph

    def reset_graph(self):
        self._ccgraph.reset()

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

    def _get_ast(self, filename, file_src, cache):
        ast = None
        if cache is not None:
            cache_key = ':'.join(['AST', filename, file_src])
            ast = cache.get(cache_key)
            if ast is None:
                ast = src_to_tree(filename, file_src)
                cache.put(cache_key, ast)
        else:
            ast = src_to_tree(filename, file_src)
        return ast
