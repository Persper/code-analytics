import subprocess
import pytest
import test.test_analytics2.helpers.callcommitgraph as ccghelper

# ODO import your call commit graph implementation(s)
from persper.analytics2.memorycallcommitgraph import MemoryCallCommitGraph
from persper.util.path import root_path


def test_memory_call_commit_graph():
    ccg = MemoryCallCommitGraph()
    ccghelper.test_call_commit_graph(ccg)
    serialized = ccg.serialize()
    print("Serialized:", serialized)
    assert isinstance(serialized, str)
    ccg2 = MemoryCallCommitGraph.deserialize(serialized)
    ccghelper.assert_graph_same(ccg, ccg2)

# TODO add tests for other ICallCommitGraph implementations.
