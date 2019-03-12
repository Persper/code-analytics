import os
import pytest
import subprocess
import shutil
from persper.analytics.c import CGraphServer
from persper.analytics.analyzer import Analyzer
from persper.analytics.graph_server import GO_FILENAME_REGEXES
from persper.analytics.go import GoGraphServer
from persper.util.path import root_path
server_port = 9089
server_addr = ':%d' % server_port

@pytest.fixture(scope='module')
def az():
    # build the repo first if not exists yet
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
async def test_analyzer_master_only(az):
    await az.analyze(from_beginning=True)
    az._graph_server.reset_graph()
    az.analyze()
    ccgraph = az.get_graph()
    history_truth = {
            'A': {
                'main.go::funcA': 3,
                'main.go::main': 2
                },
            'B': {'main.go::funcA': 0,
                'main.go::main': 1},
            'C': {'main.go::funcA': 0,
                'main.go::main': 1
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
                'main.go::funcA': 0,
                'main.go::main': 1,   
           }, 
            'M': {'main.go::funcA': 1,
                'main.go::main': 3
            },
            'N': {'main.go::funcA': 0,
                'main.go::main': 0},
        }
    commits = ccgraph.commits()
    for func, data in ccgraph.nodes(data=True):
        history = data['history']
        for cindex, csize in history.items():
            commit_message = commits[int(cindex)]['message']
            assert (csize == history_truth[commit_message.strip()][func])


    edges_added_by_A = set([        ])
    edges_added_by_B = set([('main.go::main','main.go::funcA'),])
    edges_added_by_C = set([
        ])
    edges_added_by_D = set([
           ('main.go::main','main.go::funcB')
        ])
    edges_added_by_E = set([
        ])
    edges_added_by_F = set([
        ('main.go::main','main.go::return_1'),
        ])
    edges_added_by_G = set([
        ('main.go::main','main.go:Rect:Abs'),
        ])        
    edges_added_by_H = set([
        ('main.go:Rect:Abs', 'main.go::funcA'),
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
    assert (set(az._graph_server.get_graph().edges()) == all_edges)
