"""
This module contains the abstractions of providers for various metrics we want to conclude from the analysis.

The abstractions don't put restriction on where to get the underlying data (e.g. must from `IReadOnlyCallCommitGraph`),
in the hope that in the future, the metrics can be evaluated on a remote database (e.g. with Stored Procedure
or something simular), and transported back to the local site. This may significant reduce the network traffic.

However, these abstractions assume the resulting metrics are representable by object model in the memory
(i.e. not too large to be held in memory). The responsibility for persisting these objects is on the user
of these interfaces, such as `DevRankAnalyzer` and `ModularityAnalyzer`.
"""
from typing import Dict, Set
from abc import ABC, abstractmethod


class IDevRankProvider(ABC):
    """
    Provides DevRank metrics.
    """
    @abstractmethod
    def get_commit_devranks(self, alpha, black_set: Set[str] = None) -> Dict[str, float]:
        """
        Computes all commits' devranks from function-level devranks
            Here is the formula:

                dr(c) = sum(dr(c, f) for f in C_f)

            where dr(*) is the devrank function, dev_eq(*, *) is the development equivalent function,
            and C_f is the set of functions that commit c changed.

        Args:
                alpha - A float between 0 and 1, commonly set to 0.85
            black_set - A set of commit hexshas to be blacklisted

        Returns:
            A dict with keys being commit hexshas and values being commit devranks

                Note: all commits are guaranteed to be present in the returned dict,
                even if their devrank is 0 or they're present in the `black_set`
        """
        return {"dummy": 0.1}

    @abstractmethod
    def get_developer_devranks(self, alpha, black_set: Set[str] = None) -> Dict[str, float]:
        """
        Args:
                alpha - A float between 0 and 1, commonly set to 0.85
            black_set - A set of commit hexshas to be blacklisted
        """
        return {"dummy": 0.1}


class IModularityScoreProvider(ABC):
    """
    Provides modularity metrics.
    """
    @abstractmethod
    def get_modularity_score(self) -> float:
        """
        Compute modularity score based on function graph.

        Returns
        -------
            modularity : float
                The modularity score of this graph.
        """
        return 0.1
