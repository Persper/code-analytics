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
    def __init__(self, graphBaselineDumpPath: str = None, graphTestDumpPath: str = None, dumpOnlyOnError: bool = True):
        super().__init__()
        if graphBaselineDumpPath:
            self._baselinePath = Path(graphBaselineDumpPath).resolve()
            self._baselinePath.mkdir(parents=True, exist_ok=True)
        else:
            self._baselinePath = None
        if graphTestDumpPath:
            self._dumpPath = Path(graphTestDumpPath).resolve()
            self._dumpPath.mkdir(parents=True, exist_ok=True)
        else:
            self._dumpPath = None
        self._dumpOnlyOnError = dumpOnlyOnError

    def onAfterCommit(self, analyzer: Analyzer, index: int, commit: Commit, isMaster: bool):
        graph: CallCommitGraph = analyzer.get_graph()

        def dumpGraph(warnIfNotAvailable: bool):
            if not self._dumpPath:
                if warnIfNotAvailable:
                    _logger.warning(
                        "Cannot dump call commit graph because no dump path has been specified. Commit %s: %s.", commit.hexsha, commit.message)
                return False
            data = networkx.readwrite.json_graph.node_link_data(graph._digraph)
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
                data = None
                with open(graphPath, "rt") as f:
                    data = json.load(f)
                baseline = networkx.readwrite.json_graph.node_link_graph(data)
                assert commitGraphEquals(baseline, graph._digraph), str.format(
                    "Graph not equvalent. Commit: {0}: {1}.", commit.hexsha, commit.message)
            except:
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
            "./feature_branch", "./feature_branch/test")
        await analyzer.analyze(from_beginning=True)
