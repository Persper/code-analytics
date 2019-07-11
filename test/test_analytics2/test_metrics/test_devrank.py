from typing import Dict, Union

import pytest

from persper.analytics2.abstractions.callcommitgraph import Node, NodeId
from persper.analytics2.memorycallcommitgraph import MemoryCallCommitGraph
from persper.analytics2.metrics.devrank import DevRankNodeResult, devrank


def extract_devrank(result: Union[DevRankNodeResult, Dict[NodeId, DevRankNodeResult]]):
    if isinstance(result, dict):
        return dict(((k, v.devrank) for (k, v) in result.items()))
    return result.devrank


def test_devrank():
    ccg = MemoryCallCommitGraph()
    node1 = NodeId("node1", "unk")
    node2 = NodeId("node2", "unk")
    node3 = NodeId("node3", "unk")
    node4 = NodeId("node4", "unk")
    weights = {node1: 10, node2: 10, node3: 10, node4: 10}

    def get_weight(node: Node):
        return weights[node.node_id]

    ccg.add_edge(node1, node2, "-")
    ccg.add_edge(node2, node1, "-")
    assert extract_devrank(devrank(ccg, get_weight)) == {node1: 0.5, node2: 0.5}

    ccg = MemoryCallCommitGraph()
    ccg.add_edge(node1, node2, "-")
    ccg.add_edge(node2, node3, "-")
    ccg.add_edge(node3, node4, "-")
    ccg.add_edge(node4, node1, "-")
    assert extract_devrank(devrank(ccg, get_weight)) == {node1: 0.25, node2: 0.25, node3: 0.25, node4: 0.25}

    ccg = MemoryCallCommitGraph()
    ccg.add_edge(node1, node2, "-")
    dr = extract_devrank(devrank(ccg, get_weight, alpha=1.0))
    assert dr[node1] == pytest.approx(0.33333, rel=1e-4)
    assert dr[node2] == pytest.approx(0.66666, rel=1e-4)
