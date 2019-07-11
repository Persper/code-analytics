from typing import Iterable, Union

from persper.analytics2.abstractions.callcommitgraph import IWriteOnlyCallCommitGraph, NodeId

__all__ = ["NodeHistoryAccumulator", "NodeFilesAccumulator"]


class NodeHistoryAccumulator():
    """
    Provides convenient methods for accumulating node history.
    (i.e. the added/removed lines to the same node in a single commit)
    """

    def __init__(self, is_logical_units: bool = False):
        """
        params
            is_logical_units: whether the accumulated "lines" are actually "logical units".
                                This will affect the behavior of `apply` method.
        """
        self._logical_units = is_logical_units
        # [NodeId]: [added_lines, removed_lines]
        self._nodes = {}

    def clear(self):
        """
        Clears all the accumulated histroy information contained in this instance.
        """
        self._nodes.clear()

    def add(self, node_id: NodeId, added_lines: int = 0, removed_lines: int = 0):
        """
        Accumulates the added/removed lines of code to the specific node_id.
        """
        info = self._nodes.get(node_id, None)
        if info == None:
            if not isinstance(node_id, NodeId):
                raise ValueError("node_id should be NodeId.")
            if not isinstance(added_lines, int):
                raise ValueError("added_lines should be int.")
            if not isinstance(removed_lines, int):
                raise ValueError("removed_lines should be int.")
            if added_lines != 0 or removed_lines != 0:
                info = [added_lines, removed_lines]
                self._nodes[node_id] = info
        else:
            info[0] += added_lines
            info[1] += removed_lines

    def get(self, node_id: NodeId):
        """
        Gets the accumulated added/removed lines of code for the specified node ID.
        returns
            (added_lines: int, removed_lines: int)
        """
        info = self._nodes.get(node_id, None)
        if info == None:
            if not isinstance(node_id, NodeId):
                raise ValueError("node_id should be NodeId.")
            return 0, 0
        return info[0], info[1]

    def apply(self, graph: IWriteOnlyCallCommitGraph, commit_hexsha: str):
        """
        Applies the node history contained in this instance to the specified call commit graph,
        determined by the value of `is_logical_units` when constructing the instance.
        params
            graph: the call commit graph to be updated.
            commit_hexsha: When updating the call commit graph, specify the current commit hexsha.
        remarks
            You may want to call `clear` to reset the change history after calling this method. 
        """
        if self._logical_units:
            for id, (added, removed) in self._nodes:
                graph.update_node_history_lu(id, commit_hexsha, added, removed)
        else:
            for id, (added, removed) in self._nodes:
                graph.update_node_history(id, commit_hexsha, added, removed)


class NodeFilesAccumulator():
    """
    Provides convenient methods for tracking file operations through the commits,
    keep record of all the files containing a specific node.
    """

    def __init__(self):
        self._nodes = {}

    def clear(self):
        self._nodes.clear()

    def put(self, node_id: NodeId, added_files: Union[str, Iterable[str]] = None, removed_files: Union[str, Iterable[str]] = None):
        """
        Declares the specific files containing the specific node has been added and/or removed.
        """
        if not added_files and not removed_files:
            return
        files = self._nodes.get(node_id, None)
        if files == None:
            files = set()
            self._nodes[node_id] = files
        if added_files:
            if isinstance(added_files, str):
                files.add(added_files)
            else:
                files.update(added_files)
        if removed_files:
            if isinstance(removed_files, str):
                try:
                    files.remove(removed_files)
                except KeyError:
                    # e.g. Removing function while renaming file.
                    pass
            else:
                files.difference_update(removed_files)

    def get(self, node_id: NodeId):
        """
        Gets the files where the specified node is defined.
        returns
            a collection of file names. Do not modify the returned collection, or there will be undefined behavior.
        """
        return self._nodes.get(node_id, ())

    def apply(self, graph: IWriteOnlyCallCommitGraph, commit_hexsha: str):
        """
        Applies the nodes and their containing file information into the specific call commit graph.
        """
        for id, files in self._nodes.items():
            graph.update_node_files(id, commit_hexsha, files)
