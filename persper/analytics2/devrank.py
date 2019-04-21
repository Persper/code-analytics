from typing import Iterable

from .abstractions.analyzers import (AnalysisStatus, ICommitAnalyzer,
                                     IPostAnalyzer)
from .abstractions.callcommitgraph import (IGraphServer,
                                           IReadOnlyCallCommitGraph,
                                           IWriteOnlyCallCommitGraph)
from .abstractions.repository import ICommitInfo


class CallCommitGraphAnalyzer(ICommitAnalyzer):
    def __init__(self, graph_servers: Iterable[IGraphServer], call_commit_graph: IWriteOnlyCallCommitGraph):
        assert graph_servers
        assert call_commit_graph
        self._graph_servers = list(graph_servers)
        self._call_commit_graph = call_commit_graph

    def analyze(self, commit: ICommitInfo):
        raise NotImplementedError()


class DevRankAnalyzer(IPostAnalyzer):
    def __init__(self, call_commit_graph: IReadOnlyCallCommitGraph):
        assert call_commit_graph
        self._call_commit_graph = call_commit_graph

    def analyze(self, status: AnalysisStatus):
        pass
