import json
import logging
import os
import subprocess
from pathlib import Path
from tempfile import mkdtemp
from .utility.graph_baseline import GraphDumpAnalyzerObserver

import networkx.readwrite.json_graph
import pytest
from git import Commit
from networkx import Graph
from networkx.algorithms.isomorphism import is_isomorphic

from persper.analytics.analyzer import Analyzer
from persper.analytics.call_commit_graph import CallCommitGraph
from persper.analytics.lsp_graph_server.ccls import CclsGraphServer
from persper.util.path import root_path

_logger = logging.getLogger()

testDataRoot = os.path.dirname(os.path.abspath(__file__))


async def createFeatureBranchAnalyzer(repoName: str):
    # build the repo first if not exists yet
    repo_path = os.path.join(root_path, 'repos/' + repoName)
    script_path = os.path.join(root_path, 'tools/repo_creater/create_repo.py')
    test_src_path = os.path.join(root_path, 'test/' + repoName)
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


@pytest.mark.asyncio
async def testFeatureBranch():
    graphServer, analyzer = await createFeatureBranchAnalyzer("test_feature_branch")
    graphServer: CclsGraphServer
    analyzer: Analyzer
    async with graphServer:
        analyzer.observer = GraphDumpAnalyzerObserver(
            os.path.join(testDataRoot, "baseline/feature_branch"),
            os.path.join(testDataRoot, "actualdump/feature_branch"))
        await analyzer.analyze(from_beginning=True)

@pytest.mark.asyncio
async def testCppTestRepo():
    graphServer, analyzer = await createFeatureBranchAnalyzer("cpp_test_repo")
    graphServer: CclsGraphServer
    analyzer: Analyzer
    async with graphServer:
        analyzer.observer = GraphDumpAnalyzerObserver(
            os.path.join(testDataRoot, "baseline/cpp_test_repo"),
            os.path.join(testDataRoot, "actualdump/cpp_test_repo"))
        await analyzer.analyze(from_beginning=True)
