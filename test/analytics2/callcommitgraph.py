import os.path
import subprocess
import test.analytics2.abstractions.callcommitgraph as ccghelper

#   TODO import your call commit graph implementation(s)
# from persper.analytics2.callcommitgraph import InMemoryCallCommitGraph
from persper.util.path import root_path


def test_in_memory_call_commit_graph():
    ccg = None
    #   TODO create an instance for testing
    #ccg = InMemoryCallCommitGraph()
    ccghelper.test_call_commit_graph(ccg)
