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

from persper.analytics.analyzer2 import Analyzer
from persper.analytics.call_commit_graph import CallCommitGraph, CommitIdGenerators
from persper.analytics.lsp_graph_server.ccls import CclsGraphServer
from persper.util.path import root_path

_logger = logging.getLogger()

testDataRoot = os.path.dirname(os.path.abspath(__file__))


def prepareRepo(repoName: str):
    # build the repo first if not exists yet
    repo_path = os.path.join(root_path, 'repos/' + repoName)
    script_path = os.path.join(root_path, 'tools/repo_creater/create_repo.py')
    test_src_path = os.path.join(root_path, 'test/' + repoName)
    if not os.path.isdir(repo_path):
        cmd = '{} {}'.format(script_path, test_src_path)
        subprocess.call(cmd, shell=True)
    print("Repository path: ", repo_path)
    return repo_path


def createCclsGraphServer():
    # create workspace root folder
    CCLS_COMMAND = os.path.join(root_path, "bin/ccls")
    DUMP_LOGS = False
    workspaceRoot = mkdtemp()
    print("Workspace root: ", workspaceRoot)
    graphServer = CclsGraphServer(workspaceRoot, cacheRoot="./.ccls-cache",
                                  languageServerCommand=CCLS_COMMAND +
                                  (" -log-file=ccls.log" if DUMP_LOGS else ""),
                                  dumpLogs=DUMP_LOGS,
                                  graph=CallCommitGraph(commit_id_generator=CommitIdGenerators.fromComment))
    graphServer.reset_graph()
    return graphServer


@pytest.mark.asyncio
async def testFeatureBranchFirstParent():
    """
    Tests test_feature_branch repos, only on topical branch.
    """
    repoPath = prepareRepo("test_feature_branch")
    graphServer = createCclsGraphServer()
    analyzer = Analyzer(repoPath, graphServer, firstParentOnly=True)
    async with graphServer:
        analyzer.observer = GraphDumpAnalyzerObserver(
            os.path.join(testDataRoot, "baseline/feature_branch_first_parent"),
            os.path.join(testDataRoot, "actualdump/feature_branch_first_parent"))
        await analyzer.analyze()


@pytest.mark.asyncio
async def testFeatureBranch():
    """
    Tests test_feature_branch repos, on all branches.
    """
    repoPath = prepareRepo("test_feature_branch")
    graphServer = createCclsGraphServer()
    analyzer = Analyzer(repoPath, graphServer, firstParentOnly=False)
    async with graphServer:
        analyzer.observer = GraphDumpAnalyzerObserver(
            os.path.join(testDataRoot, "baseline/feature_branch"),
            os.path.join(testDataRoot, "actualdump/feature_branch"))
        await analyzer.analyze()


@pytest.mark.asyncio
async def testCppTestRepo():
    repoPath = prepareRepo("cpp_test_repo")
    graphServer = createCclsGraphServer()
    analyzer = Analyzer(repoPath, graphServer)
    async with graphServer:
        analyzer.observer = GraphDumpAnalyzerObserver(
            os.path.join(testDataRoot, "baseline/cpp_test_repo"),
            os.path.join(testDataRoot, "actualdump/cpp_test_repo"))
        await analyzer.analyze()
