import os
import pytest
import shutil
import subprocess
from persper.analytics.graph_server import GO_FILENAME_REGEXES
from persper.analytics.go import GoGraphServer
from persper.analytics.analyzer2 import Analyzer
from persper.util.path import root_path
from .utility.go_graph_server import GoGraphBackend

GO_GRAPH_SERVER_PORT = 9089


@pytest.fixture(scope = 'module')
def az():
    """ Build the test repo if not already exists

    Args:
            repo_path - A string, path to the to-be-built test repo
          script_path - A string, path to the repo creator script
        test_src_path - A string, path to the dir to be passed to repo creator
    """
    repo_path = os.path.join(root_path, 'repos/go_test_package')
    script_path = os.path.join(root_path, 'tools/repo_creater/create_repo.py')
    test_src_path = os.path.join(root_path, 'test/go_test_package')
    server_address = 'http://127.0.0.1:%d' % GO_GRAPH_SERVER_PORT

    # Always use latest source to create test repo
    if os.path.exists(repo_path):
        shutil.rmtree(repo_path)

    cmd = '{} {}'.format(script_path, test_src_path)
    subprocess.call(cmd, shell = True)

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
    await az.analyze()
    ccgraph = az.graph
    history_truth = {
        'A': {
            'calcproj/src/simplemath/add.go::Add': {'adds': 3, 'dels': 0},
            'calcproj/src/simplemath/add_test.go::TestAdd1': {'adds': 7, 'dels': 0},
            'calcproj/src/simplemath/sqrt.go::Sqrt': {'adds': 4, 'dels': 0},
            'calcproj/src/simplemath/sqrt_test.go::TestSqrt1': {'adds': 7, 'dels': 0},

        },
        'B': {
            'calcproj/src/calc/calc.go::main': {'adds': 41, 'dels': 0},
        },
    }

    commits = ccgraph.commits()
    for func, data in ccgraph.nodes(data = True):
        history = data['history']
        for csha, csize in history.items():
            commit_message = commits[csha]['message']
            print(commit_message.strip())
            print(func)
            assert (csize == history_truth[commit_message.strip()][func])

    edges_added_by_A = set([
        ('calcproj/src/simplemath/sqrt.go::Sqrt', 'calcproj/src/simplemath/sqrt.go::Sqrt'),
        ('calcproj/src/simplemath/add_test.go::TestAdd1', 'calcproj/src/simplemath/add.go::Add'),
        ('calcproj/src/simplemath/sqrt_test.go::TestSqrt1', 'calcproj/src/simplemath/sqrt.go::Sqrt'),
    ])

    edges_added_by_B = set([
        ('calcproj/src/calc/calc.go::main', 'calcproj/src/simplemath/add.go::Add'),
        ('calcproj/src/calc/calc.go::main', 'calcproj/src/simplemath/sqrt.go::Sqrt'),
    ])
    all_edges = edges_added_by_A.union(edges_added_by_B)
    assert(set(ccgraph.edges()) == all_edges)
