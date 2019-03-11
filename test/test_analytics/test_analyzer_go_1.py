import os
import time
import pytest
import shutil
import subprocess
from persper.analytics.graph_server import GO_FILENAME_REGEXES
from persper.analytics.go import GoGraphServer
from persper.analytics.analyzer import Analyzer
from persper.util.path import root_path

# TODO: Use a port other than the default 8080 in case of collision
server_port = 8080


@pytest.fixture(scope='module')
def az():
    """ Build the test repo if not already exists

    Args:
            repo_path - A string, path to the to-be-built test repo
          script_path - A string, path to the repo creator script
        test_src_path - A string, path to the dir to be passed to repo creator
    """
    repo_path = os.path.join(root_path, 'repos/go_test_repo_1')
    script_path = os.path.join(root_path, 'tools/repo_creater/create_repo.py')
    test_src_path = os.path.join(root_path, 'test/go_test_repo_1')
    server_addr = 'http://localhost:%d' % server_port

    # Always use latest source to create test repo
    if os.path.exists(repo_path):
        shutil.rmtree(repo_path)

    cmd = '{} {}'.format(script_path, test_src_path)
    subprocess.call(cmd, shell=True)

    return Analyzer(repo_path, GoGraphServer(server_addr, GO_FILENAME_REGEXES))


def test_analzyer_go(az):
    az._graph_server.reset_graph()
    az.analyze()
    ccgraph = az.get_graph()

    history_truth = {
        'B': {'Abs': 3,
              'funcA': 0,
              'funcB': 3,
              'main': 5},
        'A': {'Abs': 3,
              'funcA': 3,
              'main': 6}
    }

    commits = ccgraph.commits()
    for func, data in ccgraph.nodes(data=True):
        history = data['history']
        for cindex, csize in history.items():
            commit_message = commits[int(cindex)]['message']
            assert csize == history_truth[commit_message.strip()][func]

    edges_added_by_A = set([
        ('Abs', 'Sqrt'),
        ('funcA', 'Println'),
        ('main', 'a'),
        ('main', 'Println'),
        ('main', 'Abs'),
    ])

    edges_added_by_B = set([
        ('Abs', 'funcA'),
        ('funcB', 'Println'),
        ('main', 'b'),
        ('main', 'c'),
    ])


    all_edges = edges_added_by_A.union(edges_added_by_B)
    assert set(az._graph_server.get_graph().edges()) == all_edges
