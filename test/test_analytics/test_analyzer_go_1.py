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
<<<<<<< HEAD
    graph_server_bin = build_graph_server()
    graph_server_proc = run_graph_server(graph_server_bin)

    try:
        az._graph_server.reset_graph()
        az.analyze()
        ccgraph = az.get_graph()


        history_truth = {
            'B': {
                'calcproj/src/simplemath/add_test.go::TestAdd1': 0,
                'calcproj/src/simplemath/add.go::Add': 0,
                'calcproj/src/simplemath/sqrt_test.go::TestSqrt1': 0,
                'calcproj/src/simplemath/sqrt.go::Sqrt': 0,
                'calcproj/src/calc/calc.go::main': 41,
                'calcproj/src/calc/calc.go::Usage': 4},
            'A': {
                'calcproj/src/simplemath/add_test.go::TestAdd1': 7,
                'calcproj/src/simplemath/add.go::Add': 3,
                'calcproj/src/simplemath/sqrt_test.go::TestSqrt1': 7,
                'calcproj/src/simplemath/sqrt.go::Sqrt': 4} #### maybe 3
        }


        commits = ccgraph.commits()
        for func, data in ccgraph.nodes(data=True):
            history = data['history']
            for cindex, csize in history.items():
                commit_message = commits[int(cindex)]['message']
                assert (csize == history_truth[commit_message.strip()][func])

        edges_added_by_A = set([
            ('calcproj/src/simplemath/sqrt_test.go::TestSqrt1', 'calcproj/src/simplemath/sqrt.go::Sqrt'),
            ('calcproj/src/simplemath/add_test.go::TestAdd1', 'calcproj/src/simplemath/add.go::Add'),
            ('calcproj/src/simplemath/sqrt.go::Sqrt', 'calcproj/src/simplemath/sqrt.go::Sqrt'),
        ])

        edges_added_by_B = set([      
            ('calcproj/src/calc/calc.go::main', 'calcproj/src/calc/calc.go::Usage'),  #should have this edge
            ('calcproj/src/calc/calc.go::main', 'calcproj/src/simplemath/add.go::Add'),    
            ('calcproj/src/calc/calc.go::main', 'calcproj/src/simplemath/sqrt.go::Sqrt')   
        ])

        all_edges = edges_added_by_A.union(edges_added_by_B)
        assert (set(az._graph_server.get_graph().edges()) == all_edges)

    finally:
        graph_server_proc.terminate()
=======
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
>>>>>>> c57baf152dc3a0b31a56a0487f789f54b9b43081
