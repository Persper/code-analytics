from persper.analytics2.abstractions.callcommitgraph import IWriteOnlyCallCommitGraph, NodeId


class NodeHistoryAccumulator():
    """
    Provides convenient methods for accumulating node history.
    (i.e. the added/removed lines to the same node in a single commit)
    """

    def __init__(self):
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
        Applies the node history contained in this instance to the specified call commit graph.
        params
            graph: the call commit graph to be updated.
            commit_hexsha: When updating the call commit graph, specify the current commit hexsha.
        remarks
            You may want to call `clear` to reset the change history after calling this method. 
        """
        for id, (added, removed) in self._nodes:
            graph.update_node_history(id, commit_hexsha, added, removed)
