import os
import time
import pytest
import shutil
import subprocess
import tempfile
from persper.analytics.graph_server import GO_FILENAME_REGEXES
from persper.analytics.go import GoGraphServer
from persper.analytics.analyzer import Analyzer
from persper.util.path import root_path

# TODO: Use a port other than the default 8080 in case of collision
server_port = 9089
server_addr = ':%d' % server_port


@pytest.fixture(scope = 'module')
def az():
    """ Build the test repo if not already exists

    Args:
            repo_path - A string, path to the to-be-built test repo
          script_path - A string, path to the repo creator script
        test_src_path - A string, path to the dir to be passed to repo creator
    """
    repo_path = os.path.join(root_path, 'repos/go_test_repo_package')
    script_path = os.path.join(root_path, 'tools/repo_creater/create_repo.py')
    test_src_path = os.path.join(root_path, 'test/go_test_repo_package')
    server_addr = 'http://localhost:%d' % server_port

    # Always use latest source to create test repo
    if os.path.exists(repo_path):
        shutil.rmtree(repo_path)

    cmd = '{} {}'.format(script_path, test_src_path)
    subprocess.call(cmd, shell = True)

    return Analyzer(repo_path, GoGraphServer(server_addr, GO_FILENAME_REGEXES))


def test_analzyer_go(az):
    az._graph_server.reset_graph()
    az.analyze()
    ccgraph = az.get_graph()

    history_truth = {
        'B': {
              'calcproj/src/simplemath/sqrt.go::Sqrt': {'adds': 4, 'dels': 0}, 
              'calcproj/src/simplemath/sqrt_test.go::TestSqrt1': {'adds':7, 'dels': 0},
              'calcproj/src/simplemath/add_test.go::TestAdd1': {'adds': 7, 'dels': 0}, 
              'calcproj/src/simplemath/add.go::Add': {'adds': 3, 'dels': 0},
              'calcproj/src/cals/cals.go::main': {'adds': 42, 'dels': 0},  
              }, 
        'A': {
              'calcproj/src/simplemath/sqrt.go::Sqrt': {'adds': 4, 'dels': 0}, 
              'calcproj/src/simplemath/sqrt.go::TestSqrt1': {'adds':7, 'dels': 0},
              'calcproj/src/simplemath/sqrt.go::TestAdd1': {'adds': 7, 'dels': 0}, 
              'calcproj/src/simplemath/sqrt.go::Add': {'adds': 3, 'dels': 0}, 

              }
    }

    commits = ccgraph.commits()
    for func, data in ccgraph.nodes(data = True):
        history = data['history']
        for cindex, csize in history.items():
            commit_message = commits[int(cindex)]['message']
            assert csize == history_truth[commit_message.strip()][func]

    edges_added_by_A = set([
        ('calcproj/src/simplemath/sqrt_test.go::TestSqrt1', 'calcproj/src/simplemath/sqrt.go::Sqrt'), 
        ('calcproj/src/simplemath/add_test.go::TestAdd1', 'calcproj/src/simplemath/add.go::Add'),
    ])

    edges_added_by_B = set([

    ])

    all_edges = edges_added_by_A.union(edges_added_by_B)
    assert set(az._graph_server.get_graph().edges()) == all_edges
