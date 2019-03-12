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


@pytest.fixture(scope='module')
def az():
    """ Build the test repo if not already exists

    Args:
            repo_path - A string, path to the to-be-built test repo
          script_path - A string, path to the repo creator script
        test_src_path - A string, path to the dir to be passed to repo creator
    """
    repo_path = os.path.join(root_path, 'repos/go_test_repo_temp')
    script_path = os.path.join(root_path, 'tools/repo_creater/create_repo.py')
    test_src_path = os.path.join(root_path, 'test/go_test_repo_temp')
    server_addr = 'http://localhost:%d' % server_port

    # Always use latest source to create test repo
    if os.path.exists(repo_path):
        shutil.rmtree(repo_path)

    cmd = '{} {}'.format(script_path, test_src_path)
    subprocess.call(cmd, shell=True)

    return Analyzer(repo_path, GoGraphServer(server_addr, GO_FILENAME_REGEXES))

def build_graph_server():
    temp_dir = tempfile.gettempdir()
    graph_server_src = os.path.join(temp_dir, 'merico', 'src', 'graph-server')
    graph_server_bin = os.path.join(temp_dir, 'merico', 'bin', 'graphserver')
    if not os.path.isdir(graph_server_src):
        ret = subprocess.call(
            ["git", "clone", "git@gitlab.com:meri.co/golang/graph-server.git", graph_server_src])
        if ret != 0:
            print("git clone failed")
            exit(1)
        ret = subprocess.call(
            ["git", "checkout", "-b", "fix-patch", "fix-patch-parser"],
            cwd=graph_server_src)
        if ret != 0:
            print("git checkout failed")
            exit(1)
    print("graph server src location:", graph_server_src)
    ret = subprocess.call(["git", "pull"], cwd=graph_server_src)
    if ret != 0:
        print("git pull failed")
        exit(1)
    ret = subprocess.call(
        ["go", "build", "-o", graph_server_bin, "gitlab.com/meri.co/golang/gs/app/graphserver"],
        cwd=graph_server_src)
    if ret != 0:
        print("go build failed")
        exit(1)
    print("graph server bin location:", graph_server_bin)
    return graph_server_bin


def run_graph_server(graph_server_bin):
    p = subprocess.Popen([graph_server_bin, "-addr", server_addr])
    print("graph server pid:", p.pid)
    return p


def test_analzyer_go(az):
    graph_server_bin = build_graph_server()
    graph_server_proc = run_graph_server(graph_server_bin)

    try:
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
            for cindex, csize in history.items():
                commit_message = commits[int(cindex)]['message']
                assert (csize == history_truth[commit_message.strip()][func])

        edges_added_by_A = set([
            ('main.go::main', 'main.go::funcA'),
            ('main.go::main', 'main.go:Vertex:Abs')
        ])

        edges_added_by_B = set([
           ('main.go::main','main.go::funcB'),
           ('main.go:Vertex:Abs','main.go::funcA')
        ])

        edges_added_by_C = set([
        ])
        
        edges_added_by_D = set([
            ('main.go::main','main.go:Vertex:Absp')
        ])

        edges_added_by_E = set([
            ('main.go::main','main.go:square:printInfo'),
            ('main.go::main','main.go:rectangle:printInfo')
        ])
        edges_added_by_F = set([
            ('main.go::main','main.go::invoke'),
            ('main.go::invoke','main.go:rectangle:printInfo'),
            ('main.go::invoke','main.go:square:printInfo')
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
        .union(edges_added_by_G).union(edges_added_by_H).union(edges_added_by_I).union(edges_added_by_J)
        assert (set(az._graph_server.get_graph().edges()) == all_edges)

    finally:
        graph_server_proc.terminate()

