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
    repo_path = os.path.join(root_path, 'repos/go_test_history')
    script_path = os.path.join(root_path, 'tools/repo_creater/create_repo.py')
    test_src_path = os.path.join(root_path, 'test/go_test_history')
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
            'A': {
                'main.go::funcA': 3,
                'main.go::main': 3
                },
            'B': {'main.go::funcA': 0,
                'main.go::main': 2}, ##should 1
            'C': {'main.go::funcA': 0,
                'main.go::main': 2 ###should be 1
                },
            'D': {'main.go::funcB': 3,
                'main.go::main': 1,
                'main.go::funcA': 3
                },
            'E': {
                'main.go::funcB': 0,
                'main.go::main': 0,
                'main.go::funcA': 0 
                },
            'F': {
                'main.go::funcA': 1,
                'main.go::main': 0,
            },
            'G': {
                'main.go::funcA': 1,
                'main.go::main': 0, 
            },            
            'H': {
                'main.go::funcA': 1,
                'main.go::main': 0,   
            },            
            'I': {
                'main.go::funcA': 1,
                'main.go::main': 0,   
            },           
            'J': {
                'main.go::funcA': 1,
                'main.go::main': 0,   
           }, 
            'K': {
                'main.go::funcA': 1,
                'main.go::main': 0,   
           }, 
            'L': {
                'main.go::funcA': 2,
                'main.go::main': 0,   
           }, 
            'M': {'main.go::funcA': 2,
                'main.go::main': 0,
            },
            'N': {'main.go::funcA': 2,
                'main.go::main': 0
            },
            'O': {'main.go::funcA': 0,
                'main.go::main': 0
            },
##################todo#################
            'P': {'main.go::funcA': 2,
                'main.go::main': 0
                },
            'Q': {'main.go::funcA': 2,
                'main.go::main': 0
                },            
        }

    commits = ccgraph.commits()
    for func, data in ccgraph.nodes(data=True):
        history = data['history']
        for csha, csize in history.items():
            commit_message = commits[csha]['message']
            print(commit_message.strip())
            print(func)
            print(csize)
            assert((csize['adds']+ csize['dels']) == history_truth[commit_message.strip()][func])

    edges_added_by_A = set([        ])
    edges_added_by_B = set([('main.go::main','main.go::funcA'),])
    edges_added_by_C = set([
        ])
    edges_added_by_D = set([
         ##should have   ('main.go::main','main.go::funcB')
        ])
    edges_added_by_E = set([
        ])
    edges_added_by_F = set([
  
        ])
    edges_added_by_G = set([

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
    assert(set(ccgraph.edges()) == all_edges)