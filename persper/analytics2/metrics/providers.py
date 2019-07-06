from typing import Collection, Dict

from persper.analytics2.abstractions.callcommitgraph import IReadOnlyCallCommitGraph
from persper.analytics2.abstractions.metrics import (IDevRankProvider,
                                                     IModularityScoreProvider)
from persper.analytics2.metrics.devrank import (commit_devranks,
                                                developer_devranks)


class DefaultMetricsProvider(IDevRankProvider, IModularityScoreProvider):
    """
    Default metrics provider implementation based on limited set of `IReadOnlyCallCommitGraph` API.

    remarks
        For other call commit graph implementation, such as DB-backed implementations,
        they should consider making their own DB-query-based metrics evaluation implementation
        to reduce overhead of non-performant I/O and data transfer over network.
    """

    def __init__(self, ccg: IReadOnlyCallCommitGraph):
        if not isinstance(ccg, IReadOnlyCallCommitGraph):
            raise TypeError("ccg should be assignable to IReadOnlyCallCommitGraph.")
        self._ccg = ccg

    def get_commit_devranks(self, alpha, commits_black_list: Collection[str] = None) -> Dict[str, float]:
        return commit_devranks(self._ccg, alpha, commits_black_list)

    def get_developer_devranks(self, alpha, commits_black_list: Collection[str] = None) -> Dict[str, float]:
        return developer_devranks(self._ccg, alpha, commits_black_list)

    def get_modularity_score(self) -> float:
        return NotImplemented
