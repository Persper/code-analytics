import logging

from persper.analytics2.abstractions.analyzers import (
    AnalysisStatus, CommitAnalysisStopReason, ICommitAnalyzer, IPostAnalyzer)
from persper.analytics2.abstractions.metrics import IDevRankProvider, IModularityScoreProvider

_logger = logging.getLogger(__name__)


class DevRankAnalyzer(IPostAnalyzer):
    def __init__(self, metrics_provider: IDevRankProvider):
        assert metrics_provider
        self._metrics_provider = metrics_provider

    def analyze(self, status: AnalysisStatus):
        if status.stop_reason == CommitAnalysisStopReason.FatalError:
            return
        commit_devranks = self._metrics_provider.get_commit_devranks(0.1)
        developer_devranks = self._metrics_provider.get_developer_devranks(0.1)
        # TODO persist metrics results.
        print("Developer DevRanks:", developer_devranks)

class ModularityAnalyzer(IPostAnalyzer):
    def __init__(self, metrics_provider: IModularityScoreProvider):
        assert metrics_provider
        self._metrics_provider = metrics_provider

    def analyze(self, status: AnalysisStatus):
        if status.stop_reason == CommitAnalysisStopReason.FatalError:
            return
        modularity = self._metrics_provider.get_modularity_score()
        # TODO persist metrics results.
        print("Modularity:", modularity)
