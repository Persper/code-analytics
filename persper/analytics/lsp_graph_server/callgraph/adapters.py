from persper.analytics.call_commit_graph import CallCommitGraph

from . import CallGraph, CallGraphBranch


class CallCommitGraphSynchronizer(CallGraph):
    def __init__(self, callCommitGraph: CallCommitGraph):
        super().__init__()
        self._callCommitGraph = callCommitGraph

    def add(self, branch: CallGraphBranch):
        super().add(branch)
        # Use scope full name as identifier.
        self._callCommitGraph.add_node(branch.sourceScope.name)
        self._callCommitGraph.add_node(branch.definitionScope.name)
        self._callCommitGraph.add_edge(branch.sourceScope.name, branch.definitionScope.name)

    def clear(self):
        super().clear()
        self._callCommitGraph.reset()
