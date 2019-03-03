"""
Utility functions for graph-dump-based regression tests.
"""
import json
import logging
import os
from enum import Enum
from pathlib import Path

from git import Commit
from networkx import Graph

from persper.analytics.analyzer2 import Analyzer, AnalyzerObserver
from persper.analytics.call_commit_graph import CallCommitGraph
from persper.analytics.graph_server import CommitSeekingMode

_logger = logging.getLogger()

testDataRoot = os.path.dirname(os.path.abspath(__file__))


def formatEdgeId(u: str, v: str):
    return u + "|->|" + v


def graphToDict(ccg: CallCommitGraph):
    nodes = ccg.nodes(data=True)
    for name, attr in nodes:
        if "files" in attr:
            files = list(attr["files"])
            files.sort()
            attr["files"] = files
    result = {
        "nodes": dict(nodes),
        "edges": dict(((formatEdgeId(u, v), data) for (u, v, data) in ccg.edges(data=True)))
    }
    return result


def fixGraphDict(graphData: dict):
    if "nodes" in graphData:
        for id, attr in graphData["nodes"].items():
            if "files" in attr:
                attr["files"] = set(attr["files"])
    return graphData


def assertGraphMatches(baseline: dict, ccg: CallCommitGraph):
    baselineNodeIds = set(baseline["nodes"].keys())
    for id, attr in ccg.nodes(data=True):
        baselineAttr = baseline["nodes"].get(id, None)
        assert baselineAttr != None, str.format("Extra node: {0}.", id)
        assert baselineAttr == attr, str.format(
            "Node attribute mismatch: {0}. Baseline: {1}; Actual: {2}.", id, baselineAttr, attr)
        baselineNodeIds.remove(id)
    assert not baselineNodeIds, str.format(
        "Node(s) missing: %s.", baselineNodeIds)
    baselineEdgeIds = set(baseline["edges"].keys())
    for u, v, attr in ccg.edges(data=True):
        id = formatEdgeId(u, v)
        baselineAttr = baseline["edges"].get(id, None)
        assert baselineAttr != None, str.format("Extra branch: {0}.", id)
        assert baselineAttr == attr, str.format(
            "Branch attribute mismatch: {0}. Baseline: {1}; Actual: {2}.", id, baselineAttr, attr)
        baselineEdgeIds.remove(id)
    assert not baselineEdgeIds, str.format(
        "Branch(es) missing: {0}.", baselineEdgeIds)


class GraphDumpNamingRule(Enum):
    CommitMessage = 0,
    CommitHexSha = 1


class GraphDumpAnalyzerObserver(AnalyzerObserver):
    """
    An implementation of AnalyzerObserver that generates graph dump after each commit,
    and/or asserts the generated graph is the same as baseline graph dump.
    """

    def __init__(self, graphBaselineDumpPath: str = None, graphTestDumpPath: str = None,
                 dumpOnlyOnError: bool = None, dumpNaming: GraphDumpNamingRule = GraphDumpNamingRule.CommitHexSha):
        """
        Params:
            graphBaselineDumpPath: root folder of the baseline graph dump files. Set to values other than `None`
                                    to perform basline assertions after each commit.
            graphTestDumpPath: root folder to persist graph dump of observed Analyzer after each commit. This is
                                also the root folder to dump current graph if baseline assertion fails in any commit.
            dumpOnlyOnError: True: dump current graph in Analyzer only when baseline assertion fails.
                                False: dump current graph in Analyzer after each commit.
                                None: if graphBaselineDumpPath == None, same as True; otherwise, same as False.
            dumpNaming: specify how to name the graph dump files.
        Remarks:
            Set `graphBaselineDumpPath` to `None` to generate graph dump files in the folder specified in `graphTestDumpPath`,
            which can be used as `graphBaselineDumpPath` in the next run.
        """
        super().__init__()
        if graphBaselineDumpPath:
            self._baselinePath = Path(graphBaselineDumpPath).resolve()
        else:
            self._baselinePath = None
        if graphTestDumpPath:
            self._dumpPath = Path(graphTestDumpPath).resolve()
            self._dumpPath.mkdir(parents=True, exist_ok=True)
        else:
            self._dumpPath = None
        self._dumpOnlyOnError = graphBaselineDumpPath != None if dumpOnlyOnError == None else dumpOnlyOnError

    def onAfterCommit(self, analyzer: Analyzer, commit: Commit, seeking_mode: CommitSeekingMode):
        if seeking_mode == CommitSeekingMode.Rewind:
            return
        graph: CallCommitGraph = analyzer.graph

        def dumpGraph(warnIfNotAvailable: bool):
            if not self._dumpPath:
                if warnIfNotAvailable:
                    _logger.warning(
                        "Cannot dump call commit graph because no dump path has been specified. Commit %s: %s.", commit.hexsha, commit.message)
                return False
            data = graphToDict(graph)
            graphPath = self._dumpPath.joinpath(
                commit.message.strip() + ".g.json")
            with open(graphPath, "wt") as f:
                json.dump(data, f, sort_keys=True, indent=4)
            return True
        # check baseline for regression
        if self._baselinePath:
            try:
                graphPath = self._baselinePath.joinpath(
                    commit.message.strip() + ".g.json")
                baselineData: dict = None
                with open(graphPath, "rt") as f:
                    baselineData = fixGraphDict(json.load(f))
                assertGraphMatches(baselineData, graph)
            except:
                _logger.error("Failed on commit %s: %s.",
                              commit.hexsha, commit.message)
                dumpGraph(True)
                raise
        if not self._dumpOnlyOnError:
            dumpGraph(False)
