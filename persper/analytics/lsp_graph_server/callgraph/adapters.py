import logging
from pathlib import Path, PurePath
from typing import Iterable

from persper.analytics.call_commit_graph import CallCommitGraph

from . import CallGraph, CallGraphBranch
_logger = logging.getLogger(__name__)


class CallCommitGraphSynchronizer(CallGraph):
    def __init__(self, callCommitGraph: CallCommitGraph):
        super().__init__()
        self._callCommitGraph = callCommitGraph

    def add(self, branch: CallGraphBranch):
        if branch.sourceScope == branch.definitionScope:
            # e.g. variable referernces.
            return
        if branch.sourceScope is None or branch.definitionScope is None:
            _logger.debug("Ignored branch with None scope: %s", branch)
            return
        # assuming the referenced edges has already been registered,
        # or there will be Error
        self._callCommitGraph.add_edge(branch.sourceScope.name, branch.definitionScope.name)

    def removeBySourceFiles(self, fileNames: Iterable[PurePath]):
        pass

    def clear(self):
        self._callCommitGraph.reset()
