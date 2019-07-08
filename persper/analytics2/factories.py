from persper.analytics2.graphservers.c import CGraphServer
from persper.analytics2.memorycallcommitgraph import MemoryCallCommitGraph
from persper.analytics2.abstractions.repository import ICommitRepository
from persper.analytics2.analyzers.callcommit import CallCommitGraphAnalyzer
from persper.analytics2.analyzers.metrics import DevRankAnalyzer, ModularityAnalyzer
from persper.analytics2.metrics.providers import DefaultMetricsProvider
from persper.analytics2.metaanalyzer import MetaAnalyzer


class lazy(object):
    """
    Decorates read-only properties whose value is created only upon the first time invocation.
    """

    def __init__(self, func):
        self.func = func

    def __get__(self, instance, cls):
        val = self.func(instance)
        setattr(instance, self.func.__name__, val)
        return val


class RootContainer:
    """
    Maintains lifetime for the objects for analysis.

    This container is intended to have the same lifetime as `analytics_main` function.
    Almost all of the instances contained are singletons.
    """

    def __init__(self, i_commit_repository: "ICommitRepository"):
        self._i_commit_repository = i_commit_repository

    def ICommitRepository(self):
        return self._i_commit_repository

    @lazy
    def ICallCommitGraph(self):
        return MemoryCallCommitGraph()

    @lazy
    def CallCommitGraphAnalyzer(self):
        return CallCommitGraphAnalyzer([
            self.CPPGraphServer
        ], self.ICallCommitGraph)

    @lazy
    def _DefaultMetricsProvider(self):
        return DefaultMetricsProvider(self.ICallCommitGraph)

    @lazy
    def DevRankAnalyzer(self):
        return DevRankAnalyzer(self._DefaultMetricsProvider)

    @lazy
    def ModularityAnalyzer(self):
        return ModularityAnalyzer(self._DefaultMetricsProvider)

    @lazy
    def CGraphServer(self):
        # Consider only using CPPGraphServer below for c/cpp.
        # Analyzing with CGraphServer and CPPGraphServer can cause .h/.c files being analyzed twice. 
        return CGraphServer(self.ICallCommitGraph, "c", CGraphServer.C_FILENAME_REGEX)

    @lazy
    def CPPGraphServer(self):
        return CGraphServer(self.ICallCommitGraph, "cpp", CGraphServer.CPP_FILENAME_REGEX)
