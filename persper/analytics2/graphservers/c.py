import logging
import re

from persper.analytics2.abstractions.callcommitgraph import (
    ICommitInfo, IGraphServer, IWriteOnlyCallCommitGraph, NodeId)
from persper.analytics2.abstractions.repository import (FileDiffOperation,
                                                        ICommitInfo, IFileDiff)
from persper.analytics2.repository import FileNameRegexWorkspaceFileFilter
from persper.analytics2.utilities import NodeFilesAccumulator
from persper.analytics.call_commit_graph import CallCommitGraph
from persper.analytics.call_graph.c import get_func_ranges_c, update_graph_a2
from persper.analytics.detect_change import get_changed_functions
from persper.analytics.inverse_diff import inverse_diff
from persper.analytics.patch_parser import PatchParser
from persper.analytics.srcml import src_to_tree

_logger = logging.getLogger(__file__)


def function_change_stats(old_ast, old_src, new_ast, new_src, adds, dels, ranges_func):
    """
    Parse old/new source files and extract the change info for all functions
    """
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


class CGraphServer(IGraphServer):
    # todo(hezheng) consider moving these regexes to their corresponding language file
    C_FILENAME_REGEX = r'(?i).+\.(h|c)$'

    # http://gcc.gnu.org/onlinedocs/gcc-4.4.1/gcc/Overall-Options.html#index-file-name-suffix-71
    CPP_FILENAME_REGEX = r'(?i).+\.(c|cc|cxx|cpp|c\+\+|c|h|hh|hpp|h\+\+)$'

    def __init__(self, ccgraph: IWriteOnlyCallCommitGraph, language="cpp", filename_regex_str=None):
        self._ccgraph = ccgraph
        if filename_regex_str == None:
            filename_regex_str = CGraphServer.CPP_FILENAME_REGEX
        self._language = language
        self._file_filter = FileNameRegexWorkspaceFileFilter(filename_regex_str)
        self._pparser = PatchParser()
        self._files = NodeFilesAccumulator()

    def __repr__(self):
        return "CGraphServer({0})".format(self._language)

    def start(self):
        pass

    def update_graph(self, commit: ICommitInfo):
        # for merge commit, we diff from its first parent, and only update edges
        diff = commit.diff_from(commit.parents[0] if commit.parents else None,
                                current_commit_filter=self._file_filter, base_commit_filter=self._file_filter)

        for d in diff:
            d: IFileDiff

            old_src = d.old_file.get_content_text() if d.old_file else None
            new_src = d.new_file.get_content_text() if d.new_file else None
            old_ast = None
            new_ast = None

            # Parse source codes into ASTs
            if d.old_file:
                old_ast = src_to_tree(d.old_file.name, old_src)
                if old_ast is None:
                    _logger.warning("Failed to parse old_file: %s. Skipped.", d.old_file.name)
                    continue

            if d.new_file:
                new_ast = src_to_tree(d.new_file.name, new_src)
                if new_ast is None:
                    _logger.warning("Failed to parse new_file: %s. Skipped.", d.new_file.name)
                    continue
            # Update node history
            if len(commit.parents) <= 1:
                adds, dels = None, None
                try:
                    adds, dels = self._pparser.parse(d.patch.decode('utf-8', 'replace'))
                except Exception as ex:
                    _logger.warn("Failed to parse patch for %s. %s", repr(d), str(ex))
                change_stats = function_change_stats(old_ast, old_src, new_ast, new_src, adds, dels, get_func_ranges_c)
                hexsha = commit.hexsha
                for k in change_stats:
                    v = change_stats[k]
                    node_id = NodeId(k, self._language)
                    self._ccgraph.update_node_history(node_id, hexsha, v['adds'], v['dels'])
                    self._ccgraph.update_node_history_lu(node_id, hexsha, v['added_units'], v['removed_units'])
            # Update edges & node files
            old_file_path = d.old_file.path if d.old_file else None
            new_file_path = d.new_file.path if d.new_file else None
            update_graph_a2(self._ccgraph, self._files, commit.hexsha,
                            self._language, new_ast, old_file_path, new_file_path)

    def stop(self):
        pass
