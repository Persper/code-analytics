# -*- coding: utf-8 -*-

from persper.analytics.call_commit_graph import CallCommitGraph


def test_modularity():
    ccgraph = CallCommitGraph()
    for i in range(0, 100):
        ccgraph.add_node("node" + str(i))
    # No any edges
    assert ccgraph.compute_modularity() == 0

    # Only one edge
    ccgraph.add_edge("node0", "node1")
    assert ccgraph.compute_modularity() == 0

    # Multiple edges
    for i in range(1, 99):
        ccgraph.add_edge("node" + str(i), "node" + str(i + 1))
    assert int(ccgraph.compute_modularity()) == 80
