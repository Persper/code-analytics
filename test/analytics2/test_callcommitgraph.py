import subprocess
import pytest
from ..analytics2.abstractions import callcommitgraph as ccghelper

#   TODO import your call commit graph implementation(s)
from persper.analytics2.memorycallcommitgraph import MemoryCallCommitGraph
from persper.util.path import root_path


def test_memory_call_commit_graph():
    ccg = MemoryCallCommitGraph()
    ccghelper.test_call_commit_graph(ccg)

