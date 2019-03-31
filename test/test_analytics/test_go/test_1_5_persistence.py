import os
import pickle
import pytest
import shutil
import subprocess
from persper.analytics.graph_server import GO_FILENAME_REGEXES
from persper.analytics.go import GoGraphServer
from persper.analytics.analyzer2 import Analyzer
from persper.util.path import root_path
from test.test_analytics.utility.go_graph_server import GoGraphBackend
from test.test_analytics.utility.graph_helper import reduce_graph_history_truth, reduce_graph_edge_truth
from test.test_analytics.utility.graph_helper import reduce_graph_history_truth, reduce_graph_edge_truth

GO_GRAPH_SERVER_PORT = 9089


@pytest.fixture(scope='module')
def az():
    """ Build the test repo if not already exists

    Args:
            repo_path - A string, path to the to-be-built test repo
          script_path - A string, path to the repo creator script
        test_src_path - A string, path to the dir to be passed to repo creator
    """
    repo_path = os.path.join(root_path, 'repos/0_common')
    script_path = os.path.join(root_path, 'tools/repo_creater/create_repo.py')
    test_src_path = os.path.join(root_path, 'test/go_test_repos/0_common')
    server_address = 'http://127.0.0.1:%d' % GO_GRAPH_SERVER_PORT

    # Always use latest source to create test repo
    if os.path.exists(repo_path):
        shutil.rmtree(repo_path)

    cmd = '{} {}'.format(script_path, test_src_path)
    subprocess.call(cmd, shell=True)

    return Analyzer(repo_path, GoGraphServer(server_address, GO_FILENAME_REGEXES))


@pytest.mark.asyncio
async def test_analzyer_go(az):
    backend = GoGraphBackend(GO_GRAPH_SERVER_PORT)
    backend.build()
    backend.run()
    try:
        await _test_analzyer_go(az)
    finally:
        backend.terminate()


@pytest.mark.skip
async def _test_analzyer_go(az):
    az._graphServer.reset_graph()
    await az.analyze(2)
    ccg = az.graph
    history_truth = {
        'A': {
            'main.go:Vertex:Abs': {'adds': 3, 'dels': 0},
            'main.go::funcA': {'adds': 3, 'dels': 0},
            'main.go::main': {'adds': 6, 'dels': 0},
        },
        'B': {
            'main.go:Vertex:Abs': {'adds': 3, 'dels': 0},
            'main.go::funcA': {'adds': 0, 'dels': 0},
            'main.go::funcB': {'adds': 3, 'dels': 0},
            'main.go::main': {'adds': 4, 'dels': 1},
        },
    }
    reduced_history_truth = reduce_graph_history_truth(history_truth)
    commits = ccg.commits()
    for func, data in ccg.nodes(data=True):
        history = data['history']
        for csha, csize in history.items():
            commit_message = commits[csha]['message']
            assert (csize == reduced_history_truth[commit_message.strip()][func])
    edges_added_by_a = {
        ('main.go::main', 'main.go:Vertex:Abs')
    }
    edges_added_by_b = {
        ('main.go:Vertex:Abs', 'main.go::funcA')
    }
    all_edges = edges_added_by_a.union(edges_added_by_b)
    reduced_edges = reduce_graph_edge_truth(all_edges)
    assert (set(ccg.edges()) == reduced_edges)

    # pickle
    pickle_content = pickle.dumps(az)
    az = None
    ccg = None

    # recover
    az2: Analyzer = pickle.loads(pickle_content)
    ccg = az2.graph
    commits = ccg.commits()
    # verify existing nodes and edges
    for func, data in ccg.nodes(data=True):
        history = data['history']
        for csha, csize in history.items():
            commit_message = commits[csha]['message']
            assert (csize == reduced_history_truth[commit_message.strip()][func])
    assert (set(ccg.edges()) == reduced_edges)
    # start analyze
    await az2.analyze()
    ccg = az2.graph
    history_truth['C'] = {
        'main.go:Vertex:Abs': {'adds': 2, 'dels': 3},
        'main.go::funcB': {'adds': 1, 'dels': 0},
    }
    history_truth['D'] = {
        'main.go:Vertex:Abs': {'adds': 0, 'dels': 2},
        'main.go::funcA': {'adds': 0, 'dels': 0},
        'main.go::funcB': {'adds': 0, 'dels': 4},
        'main.go::main': {'adds': 3, 'dels': 4},
        "main.go:Vertex:Absp": {'adds': 3, 'dels': 0},
    }
    reduced_history_truth = reduce_graph_history_truth(history_truth)
    commits = ccg.commits()
    for func, data in ccg.nodes(data=True):
        history = data['history']
        for csha, csize in history.items():
            commit_message = commits[csha]['message']
            assert (csize == reduced_history_truth[commit_message.strip()][func])
    edges_added_by_c = {
        ('main.go::funcB', 'main.go::funcA')
    }
    edges_added_by_d = {
        ("main.go::main", "main.go:Vertex:Absp")
    }
    all_edges = edges_added_by_a.union(edges_added_by_b).union(edges_added_by_c).union(edges_added_by_d)
    reduced_edges = reduce_graph_edge_truth(all_edges)
    assert (set(ccg.edges()) == reduced_edges)
