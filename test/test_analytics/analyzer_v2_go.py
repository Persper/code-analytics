import os
import time
import pytest
import shutil
import subprocess
from persper.analytics.graph_server import GO_FILENAME_REGEXES
from persper.analytics.go import GoGraphServer
from persper.analytics.analyzer2 import Analyzer
from persper.util.path import root_path
import asyncio

# TODO: Use a port other than the default 8080 in case of collision
server_port = 9089


def main():
    repo_path = os.path.join(root_path, 'repos/go_test_repo')
    script_path = os.path.join(root_path, 'tools/repo_creater/create_repo.py')
    test_src_path = os.path.join(root_path, 'test/go_test_repo')
    server_addr = 'http://localhost:%d' % server_port

    # Always use latest source to create test repo
    if os.path.exists(repo_path):
        shutil.rmtree(repo_path)

    cmd = '{} {}'.format(script_path, test_src_path)
    subprocess.call(cmd, shell=True)

    az = Analyzer(repo_path, GoGraphServer(server_addr, GO_FILENAME_REGEXES))

    az._graphServer.reset_graph()
    asyncio.run(az.analyze())
    ccgraph = az.graph()

    history_truth = {
        'D': {'Abs': 6,
              'funcA': 0,
              'main': 8,
              "Absp": 3},
        'C': {'Abs': 5,
              'funcA': 0,
              'funcB': 1,
              'main': 0},
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
            assert (csize == history_truth[commit_message.strip()][func])

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

    edges_added_by_C = set([
        ('Abs', 'a'),
        ('funcB', 'funcA')
    ])

    edges_added_by_D = set([
        ("Absp", "Sqrt"),
        ("main", "Absp")
    ])

    print(set(az._graph_server.get_graph().edges()))
    all_edges = edges_added_by_A.union(edges_added_by_B).union(edges_added_by_C).union(edges_added_by_D)
    assert (set(az._graph_server.get_graph().edges()) == all_edges)


if __name__ == '__main__':
    main()
