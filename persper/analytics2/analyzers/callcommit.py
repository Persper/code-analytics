import logging
from time import monotonic
from typing import Iterable

from persper.analytics2.abstractions.analyzers import (
    AnalysisStatus, CommitAnalysisStopReason, ICommitAnalyzer, IPostAnalyzer)
from persper.analytics2.abstractions.callcommitgraph import (
    Commit, IGraphServer, IReadOnlyCallCommitGraph, IWriteOnlyCallCommitGraph)
from persper.analytics2.abstractions.repository import ICommitInfo, repr_hexsha

_logger = logging.getLogger(__name__)


class CallCommitGraphAnalyzer(ICommitAnalyzer):
    """
    Analyzes each commit with graph servers, populating the specified call commit graph.
    """
    def __init__(self, graph_servers: Iterable[IGraphServer], call_commit_graph: IWriteOnlyCallCommitGraph):
        assert graph_servers
        assert call_commit_graph
        self._graph_servers = list(graph_servers)
        self._call_commit_graph = call_commit_graph

    def analyze(self, commit: ICommitInfo):
        assert commit
        self._call_commit_graph.update_commit(Commit.from_commit_info(commit))
        for gs in self._graph_servers:
            t0 = monotonic()
            _logger.info("Analyzing %s with %s.", repr_hexsha(commit.hexsha), gs)
            assert isinstance(gs, IGraphServer)
            gs.update_graph(commit)
            _logger.info("%s finished in %.2fs.", gs, monotonic() - t0)
        t0 = monotonic()
        # We actually can flush the graph at a later stage, and reduce the frequecy of flushing.
        self._call_commit_graph.flush()
        _logger.info("Call commit graph flush used %.2fs.", monotonic() - t0)
