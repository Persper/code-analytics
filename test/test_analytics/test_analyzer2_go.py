import os
import time
import pytest
import shutil
import subprocess
from persper.analytics.graph_server import GO_FILENAME_REGEXES
from persper.analytics.go import GoGraphServer
from persper.analytics.analyzer2 import Analyzer
from persper.util.path import root_path

# TODO: Use a port other than the default 8080 in case of collision
server_port = 9089


@pytest.fixture(scope='module')
def az():
    """ Build the test repo if not already exists

    Args:
            repo_path - A string, path to the to-be-built test repo
          script_path - A string, path to the repo creator script
        test_src_path - A string, path to the dir to be passed to repo creator
    """
    repo_path = os.path.join(root_path, 'repos/go_test_repo')
    script_path = os.path.join(root_path, 'tools/repo_creater/create_repo.py')
    test_src_path = os.path.join(root_path, 'test/go_test_repo')
    server_addr = 'http://localhost:%d' % server_port

    # Always use latest source to create test repo
    if os.path.exists(repo_path):
        shutil.rmtree(repo_path)

    cmd = '{} {}'.format(script_path, test_src_path)
    subprocess.call(cmd, shell=True)

    return Analyzer(repo_path, GoGraphServer(server_addr, GO_FILENAME_REGEXES))


@pytest.mark.asyncio
async def test_analzyer_go(az):
    az._graphServer.reset_graph()
    await az.analyze()
    ccgraph = az.graph

    history_truth = {
        'D': {
            'main.go:Vertex:Abs': {'adds': 0, 'dels': 2},
            # TODO graph server bug
            # related issue https://gitlab.com/persper/code-analytics/issues/12
            'main.go::funcA': {'adds': 0, 'dels': 0},
            'main.go::funcB': {'adds': 0, 'dels': 4},
            'main.go::main': {'adds': 3, 'dels': 4},
            "main.go:Vertex:Absp": {'adds': 3, 'dels': 0},
        },
        'C': {
            'main.go:Vertex:Abs': {'adds': 2, 'dels': 3},
            'main.go::funcB': {'adds': 1, 'dels': 0},
        },
        'B': {
            'main.go:Vertex:Abs': {'adds': 3, 'dels': 0},
            # TODO graph server bug
            # related issue https://gitlab.com/persper/code-analytics/issues/12
            'main.go::funcA': {'adds': 0, 'dels': 0},
            'main.go::funcB': {'adds': 3, 'dels': 0},
            'main.go::main': {'adds': 4, 'dels': 1},
        },
        'A': {
            'main.go:Vertex:Abs': {'adds': 3, 'dels': 0},
            'main.go::funcA': {'adds': 3, 'dels': 0},
            'main.go::main': {'adds': 6, 'dels': 0},
        }
    }

    commits = ccgraph.commits()
    for func, data in ccgraph.nodes(data=True):
        history = data['history']
        for csha, csize in history.items():
            commit_message = commits[csha]['message']
            assert(csize == history_truth[commit_message.strip()][func])

    edges_added_by_a = {
        ('main.go::main', 'main.go:Vertex:Abs')
    }

    edges_added_by_b = {
        ('main.go:Vertex:Abs', 'main.go::funcA')
    }

    edges_added_by_c = {
        ('main.go::funcB', 'main.go::funcA')
    }

    edges_added_by_d = {
        ("main.go::main", "main.go:Vertex:Absp")
    }

    print(set(ccgraph.edges()))
    all_edges = edges_added_by_a.union(edges_added_by_b).union(edges_added_by_c).union(edges_added_by_d)
    assert(set(ccgraph.edges()) == all_edges)
