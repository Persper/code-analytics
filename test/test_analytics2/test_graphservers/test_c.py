from test.test_analytics2.helpers.callcommitgraph import (
    check_graph_baseline, commit_assertion_by_comment,
    set_is_generating_baseline)
from test.test_analytics2.utilities import prepare_repository

import pytest

from persper.analytics2.graphservers.c import CGraphServer
from persper.analytics2.memorycallcommitgraph import MemoryCallCommitGraph
from persper.analytics2.repository import GitRepository
from persper.analytics2.abstractions.callcommitgraph import Commit


def test_c_graph_server():
    repo = GitRepository(prepare_repository("test_feature_branch"))
    graph = MemoryCallCommitGraph()
    graph_server = CGraphServer(graph)
    graph_server.start()
    for commit in repo.enum_commits(None, "HEAD"):
        graph.update_commit(Commit.from_commit_info(commit))
        graph_server.update_graph(commit)
    graph_server.stop()
    check_graph_baseline("c_test_feature_branch", graph, commit_assertion_by_comment)
