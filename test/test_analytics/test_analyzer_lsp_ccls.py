import json
import logging
import os
import pickle
import subprocess
from pathlib import Path
from tempfile import mkdtemp

import pytest
from git import Commit
from networkx import Graph
from networkx.algorithms.isomorphism import is_isomorphic

from persper.analytics.analyzer2 import Analyzer
from persper.analytics.call_commit_graph import CallCommitGraph, CommitIdGenerators
from persper.analytics.lsp_graph_server.ccls import CclsGraphServer
from persper.util.path import root_path

from .utility.graph_baseline import GraphDumpAnalyzerObserver

# Whether we are generating graph dump baseline, rather than testing for regression.
IS_GENERATING_BASELINE = False

logging.basicConfig(level=logging.INFO)
_logger = logging.getLogger()

if IS_GENERATING_BASELINE:
    _logger.warning("We are generating graph dump baseline.")

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


def createGraphDumpAnalyzerObserver(testName: str):
    return GraphDumpAnalyzerObserver(
        None if IS_GENERATING_BASELINE else
        os.path.join(testDataRoot, "baseline/" + testName),
        os.path.join(testDataRoot, "actualdump/" + testName),
        dumpNaming=CommitIdGenerators.fromComment)


@pytest.mark.asyncio
async def testFeatureBranchFirstParent():
    """
    Tests test_feature_branch repos, only on topical branch.
    """
    repoPath = prepareRepo("test_feature_branch")
    graphServer = createCclsGraphServer()
    analyzer = Analyzer(repoPath, graphServer, firstParentOnly=True)
    async with graphServer:
        analyzer.observer = createGraphDumpAnalyzerObserver(
            "feature_branch_first_parent")
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
        analyzer.observer = createGraphDumpAnalyzerObserver("feature_branch")
        await analyzer.analyze()


@pytest.mark.asyncio
async def testCppTestRepo():
    repoPath = prepareRepo("cpp_test_repo")
    graphServer = createCclsGraphServer()
    analyzer = Analyzer(repoPath, graphServer)
    async with graphServer:
        analyzer.observer = createGraphDumpAnalyzerObserver("cpp_test_repo")
        await analyzer.analyze()


@pytest.mark.asyncio
async def testAnalyzerWithPickle():
    repoPath = prepareRepo("test_feature_branch")
    graphServer = createCclsGraphServer()
    analyzer = Analyzer(repoPath, graphServer)
    pickleContent = None
    async with graphServer:
        analyzer.observer = createGraphDumpAnalyzerObserver(
            "analyzer_pickling")
        assert len(analyzer.visitedCommits) == 0
        await analyzer.analyze(2)
        assert len(analyzer.visitedCommits) == 2
        await analyzer.analyze(2)
        assert len(analyzer.visitedCommits) == 4
        pickleContent = pickle.dumps(analyzer)

    analyzer1: Analyzer = pickle.loads(pickleContent)
    # Perhaps we need to set another temp folder for this.
    graphServer1 = analyzer1.graphServer
    analyzer1.observer = analyzer.observer
    async with graphServer1:
        assert analyzer1.visitedCommits == analyzer.visitedCommits
        await analyzer1.analyze()
