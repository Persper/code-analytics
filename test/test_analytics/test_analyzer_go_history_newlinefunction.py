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
    repo_path = os.path.join(root_path, 'repos/new_line_function')
    script_path = os.path.join(root_path, 'tools/repo_creater/create_repo.py')
    test_src_path = os.path.join(root_path, 'test/go_test_history_repo/new_line_function')
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
                'main.go::funcA': {'adds': 3, 'dels': 0}, 
                'main.go::main': {'adds': 3, 'dels': 0}
                 }, 
             'P': {
                'main.go::funcA': 2, 
                'main.go::main': 0
                }, 
            'Q': {
                'main.go::funcA': 2, 
                'main.go::main': 0
                },            
        }

    commits = ccgraph.commits()
    for func, data in ccgraph.nodes(data = True):
        history = data['history']
        for csha, csize in history.items():
            commit_message = commits[csha]['message']
            assert (csize == history_truth[commit_message.strip()][func])

    edges_added_by_A = set([('main.go::main', 'main.go::funcA')])
    edges_added_by_B = set([ ])
    edges_added_by_E = set([ ])

    all_edges = edges_added_by_A.union(edges_added_by_B).union(edges_added_by_C).union(edges_added_by_D).union(edges_added_by_E).union(edges_added_by_F) \
        .union(edges_added_by_G).union(edges_added_by_H).union(edges_added_by_I).union(edges_added_by_J).union(edges_added_by_K)\
        .union(edges_added_by_L).union(edges_added_by_M).union(edges_added_by_N)
    assert(set(ccgraph.edges()) == all_edges)
