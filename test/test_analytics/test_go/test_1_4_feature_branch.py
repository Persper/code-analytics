import os
import pytest
import shutil
import subprocess
from persper.analytics.graph_server import GO_FILENAME_REGEXES
from persper.analytics.go import GoGraphServer
from persper.analytics.analyzer2 import Analyzer
from persper.util.path import root_path
from test.test_analytics.utility.go_graph_server import GoGraphBackend
from test.test_analytics.utility.graph_helper import reduce_graph_history_truth, reduce_graph_edge_truth

GO_GRAPH_SERVER_PORT = 9089


@pytest.fixture(scope = 'module')
def az():
    """ Build the test repo if not already exists

    Args:
            repo_path - A string, path to the to-be-built test repo
          script_path - A string, path to the repo creator script
        test_src_path - A string, path to the dir to be passed to repo creator
    """
    repo_path = os.path.join(root_path, 'repos/1_4_feature_branch')
    script_path = os.path.join(root_path, 'tools/repo_creater/create_repo.py')
    test_src_path = os.path.join(root_path, 'test/go_test_repos/1_4_feature_branch')
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
            'B': {
                'main.go::funcA': {'adds': 0, 'dels': 0}, 
                'main.go::main': {'adds': 1, 'dels': 1}
                }, 
            'C': {
                'main.go::funcA': {'adds': 0, 'dels': 0}, 
                'main.go::main': {'adds': 1, 'dels': 1}
                }, 
            'D': {
                'func.go::funcB': {'adds': 3, 'dels': 0}, 
                'main.go::funcA': {'adds': 0, 'dels': 0}, 
                'main.go::main': {'adds': 2, 'dels': 1}, 
                "func.go::return_1":{'adds': 3, 'dels': 0}, 
                }, 
            'E': {
                'func.go::funcB': {'adds': 0, 'dels': 0}, 
                'main.go::funcA': {'adds': 0, 'dels': 0}, 
                'main.go::main': {'adds': 2, 'dels': 1}, 
                "func.go::return_1":{'adds': 0, 'dels': 0}, 

                }, 
            'F': {
                'func.go::funcB': {'adds': 0, 'dels': 0}, 
                'main.go::funcA': {'adds': 0, 'dels': 0}, 
                'main.go::main': {'adds': 0, 'dels': 0}, 
                "func.go::return_1":{'adds': 1, 'dels': 0}, 

            }, 
            'G': {
                'func.go::funcB': {'adds': 3, 'dels': 0}, 
                'main.go::funcA': {'adds': 0, 'dels': 0}, 
                'main.go::main': {'adds': 1, 'dels': 1}, 
                "func.go::return_1":{'adds': 3, 'dels': 0}, 
            },            
            'H': {
                'func.go::funcB': {'adds': 0, 'dels': 0}, 
                'main.go::funcA': {'adds': 0, 'dels': 0}, 
                'main.go::main': {'adds': 0, 'dels': 1}, 
                "func.go::return_1":{'adds': 0, 'dels': 0}, 

            },            
            'I': {
                'func.go::funcB': {'adds': 0, 'dels': 0}, 
                'main.go::funcA': {'adds': 0, 'dels': 0}, 
                'main.go::main': {'adds': 1, 'dels': 0}, 
                "func.go::return_1":{'adds': 0, 'dels': 0}, 

            },           
            'J': {
                'func.go::funcB': {'adds': 3, 'dels': 0}, 
                'main.go::funcA': {'adds': 0, 'dels': 0}, 
                'main.go::main': {'adds': 1, 'dels': 1}, 
                "func.go::return_1":{'adds': 4, 'dels': 0}, 

           }, 
            'K': {
                'func.go::funcB': {'adds': 0, 'dels': 0}, 
                'main.go::funcA': {'adds': 0, 'dels': 0}, 
                'main.go::main': {'adds': 0, 'dels': 1}, 
                "func.go::return_1":{'adds': 0, 'dels': 0}, 
           }, 
        }
    reduced_history_truth = reduce_graph_history_truth(history_truth)
    commits = ccgraph.commits()
    for func, data in ccgraph.nodes(data = True):
        history = data['history']
        for csha, csize in history.items():
            commit_message = commits[csha]['message']
            assert (csize == reduced_history_truth[commit_message.strip()][func])

    edges_added_by_A = set([        ])
    edges_added_by_B = set([('main.go::main', 'main.go::funcA'), ])
    edges_added_by_C = set([
        ])
    edges_added_by_D = set([
           ('main.go::main', 'func.go::funcB'), 
           ('main.go::main', 'func.go::return_1')
        ])
    edges_added_by_E = set([
        ])
    edges_added_by_F = set([
        ('main.go::main', 'func.go::return_1'), 
        ])
    edges_added_by_G = set([
        ('main.go::main', 'func.go::funcB')
        ])        
    edges_added_by_H = set([
    
        ]) 
    edges_added_by_I = set([
        ])  
    edges_added_by_J = set([
        ]) 
    edges_added_by_K = set([
        ])     
    edges_added_by_L = set([
        ]) 
    edges_added_by_M = set([
        ])     
    edges_added_by_N = set([
        ])     
    all_edges = edges_added_by_A.union(edges_added_by_B).union(edges_added_by_C).union(edges_added_by_D).union(edges_added_by_E).union(edges_added_by_F) \
        .union(edges_added_by_G).union(edges_added_by_H).union(edges_added_by_I).union(edges_added_by_J).union(edges_added_by_K)\
        .union(edges_added_by_L).union(edges_added_by_M).union(edges_added_by_N)
    reduced_edges = reduce_graph_edge_truth(all_edges)
    assert (set(ccgraph.edges()) == reduced_edges)
