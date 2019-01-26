import json
import logging
import os
import subprocess
from pathlib import Path
from tempfile import mkdtemp

import networkx.readwrite.json_graph
import pytest
from git import Commit
from networkx import Graph
from networkx.algorithms.isomorphism import is_isomorphic

from persper.analytics.analyzer import Analyzer, AnalyzerObserver
from persper.analytics.call_commit_graph import CallCommitGraph
from persper.analytics.lsp_graph_server.ccls import CclsGraphServer
from persper.util.path import root_path

_logger = logging.getLogger()


def formatEdgeId(u: str, v: str):
    return u + "|->|" + v


def graphToDict(ccg: CallCommitGraph):
    result = {
        "nodes": dict(ccg.nodes(data=True)),
        "edges": dict(((formatEdgeId(u, v), data) for (u, v, data) in ccg.edges(data=True)))
    }
    return result

def fixGraphDict(graphData: dict):
    if "nodes" in graphData:
        for id, attr in graphData["nodes"].items():
            if "history" in attr:
                attr["history"] = dict((int(k), v) for k, v in attr["history"].items())
    return graphData

def assertGraphMatches(baseline: dict, ccg: CallCommitGraph):
    baselineNodeIds = set(baseline["nodes"].keys())
    for id, attr in ccg.nodes(data=True):
        baselineAttr = baseline["nodes"].get(id, None)
        assert baselineAttr != None, str.format("Extra node: {0}.", id)
        assert baselineAttr == attr, str.format(
            "Node attribute mismatch: {0}. Baseline: {1}; Test: {2}.", id, baselineAttr, attr)
        baselineNodeIds.remove(id)
    assert not baselineNodeIds, str.format(
        "Node(s) missing: %s.", baselineNodeIds)
    baselineEdgeIds = set(baseline["edges"].keys())
    for u, v, attr in ccg.edges(data=True):
        id = formatEdgeId(u, v)
        baselineAttr = baseline["edges"].get(id, None)
        assert baselineAttr != None, str.format("Extra branch: {0}.", id)
        assert baselineAttr == attr, str.format(
            "Branch attribute mismatch: {0}. Baseline: {1}; Test: {2}.", id, baselineAttr, attr)
        baselineEdgeIds.remove(id)
    assert not baselineEdgeIds, str.format(
        "Branch(es) missing: {0}.", baselineEdgeIds)


def commitGraphEquals(g1: Graph, g2: Graph):
    def nodeComparer(n1: dict, n2: dict):
        if n1 == n2:
            return True
        _logger.warn(str.format("Node mismatch: n1 = {0}, n2 = {1}", n1, n2))
        return False

    def edgeComparer(e1: dict, e2: dict):
        if e1 == e2:
            return True
        _logger.warn(str.format("Edge mismatch: e1 = {0}, e2 = {1}", e1, e2))
        return False
    return is_isomorphic(g1, g2, nodeComparer, edgeComparer)


async def createFeatureBranchAnalyzer():
    # build the repo first if not exists yet
    repo_path = os.path.join(root_path, 'repos/test_feature_branch')
    script_path = os.path.join(root_path, 'tools/repo_creater/create_repo.py')
    test_src_path = os.path.join(root_path, 'test/test_feature_branch')
    if not os.path.isdir(repo_path):
        cmd = '{} {}'.format(script_path, test_src_path)
        subprocess.call(cmd, shell=True)

    # create workspace root folder
    CCLS_COMMAND = os.path.join(root_path, "bin/ccls")
    DUMP_LOGS = False
    workspaceRoot = mkdtemp()
    print("Workspace root: ", workspaceRoot)
    graphServer = CclsGraphServer(workspaceRoot, cacheRoot="./.ccls-cache",
                                  languageServerCommand=CCLS_COMMAND +
                                  (" -log-file=ccls.log" if DUMP_LOGS else ""),
                                  dumpLogs=DUMP_LOGS)
    print(repo_path)
    analyzer = Analyzer(repo_path, graphServer)
    graphServer.reset_graph()
    return graphServer, analyzer


class TestAnalyzerObserver(AnalyzerObserver):
    def __init__(self, graphBaselineDumpPath: str = None, graphTestDumpPath: str = None, dumpOnlyOnError: bool = None):
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

    def onAfterCommit(self, analyzer: Analyzer, index: int, commit: Commit, isMaster: bool):
        graph: CallCommitGraph = analyzer.get_graph()

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


@pytest.mark.asyncio
async def testFeatureBranch():
    graphServer, analyzer = await createFeatureBranchAnalyzer()
    graphServer: CclsGraphServer
    analyzer: Analyzer
    async with graphServer:
        analyzer.observer = TestAnalyzerObserver(
            "./baseline/feature_branch", "./testdump/feature_branch")
        await analyzer.analyze(from_beginning=True)
