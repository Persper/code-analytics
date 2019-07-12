import logging
from typing import Dict

from persper.analytics2.abstractions.analyzers import (
    AnalysisStatus, CommitAnalysisStopReason, ICommitAnalyzer, IPostAnalyzer)
from persper.analytics2.abstractions.metrics import (IDevRankProvider,
                                                     IModularityScoreProvider)

_logger = logging.getLogger(__name__)


class DevRankAnalyzer(IPostAnalyzer):
    """
    Analyzes for DevRank metrics.

    You should implement this class, overriding persist_results method.
    """

    def __init__(self, metrics_provider: IDevRankProvider):
        assert metrics_provider
        self._metrics_provider = metrics_provider

    def analyze(self, status: AnalysisStatus):
        if status.stop_reason == CommitAnalysisStopReason.FatalError:
            return
        commit_devranks = self._metrics_provider.get_commit_devranks(0.1)
        developer_devranks = self._metrics_provider.get_developer_devranks(0.1)
        self.persist_result(commit_devranks, developer_devranks)

    def persist_result(self, commit_devranks: Dict[str, float], developer_devranks: Dict[str, float]):
        """
        When implemented in the derived class, persists metrics results.
        The default implementation is simply printing them out.

        remarks
            Implementor may inject required services, e.g. ORM or such interface from __init__().
        """
        print("Commit DevRanks:", commit_devranks)
        print("Developer DevRanks:", developer_devranks)


class ModularityAnalyzer(IPostAnalyzer):
    """
    Analyzes for modulariy metrics.

    You should implement this class, overriding persist_results method.
    """

    def __init__(self, metrics_provider: IModularityScoreProvider):
        assert metrics_provider
        self._metrics_provider = metrics_provider

    def analyze(self, status: AnalysisStatus):
        if status.stop_reason == CommitAnalysisStopReason.FatalError:
            return
        modularity_score = self._metrics_provider.get_modularity_score()
        self.persist_result(modularity_score)

    def persist_result(self, modularity_score: float):
        """
        When implemented in the derived class, persists metrics result.
        The default implementation is simply printing it out.

        remarks
            Implementor may inject required services, e.g. ORM or such interface from __init__().
        """
        print("Modularity:", modularity_score)
