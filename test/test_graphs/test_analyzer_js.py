import os
import time
import pytest
import subprocess
from persper.graphs.js import JSGraph
from persper.graphs.analyzer import Analyzer
from persper.util.path import root_path

# Use a port other than the default 3000 in case of collision
server_port = 3002
server_path = os.path.join(root_path, 'contribs/js-callgraph/src/app.js')


@pytest.fixture(scope='module')
def az():
    """ Build the test repo if not already exists

    Args:
            repo_path - A string, path to the to-be-built test repo
          script_path - A string, path to the repo creator script
        test_src_path - A string, path to the dir to be passed to repo creator
    """
    repo_path = os.path.join(root_path, 'repos/js_test_repo')
    script_path = os.path.join(root_path, 'tools/repo_creater/create_repo.py')
    test_src_path = os.path.join(root_path, 'test/js_test_repo')
    server_addr = 'http://localhost:%d' % server_port

    if not os.path.isdir(repo_path):
        cmd = '{} {}'.format(script_path, test_src_path)
        subprocess.call(cmd, shell=True)

    return Analyzer(repo_path, JSGraph(server_addr))


def assert_graph_match_history(analyzer):
    # total edits data stored in the graph should match analyzer.history
    G = analyzer.ccg.get_graph()
    for fid in G.nodes():
        print(fid)
        total_edits = 0
        for sha in analyzer.history:
            if fid in analyzer.history[sha]:
                total_edits += analyzer.history[sha][fid]
        assert(total_edits == G.node[fid]['num_lines'])


def test_az(az):
    my_env = os.environ.copy()
    my_env["PORT"] = str(server_port)
    proc = subprocess.Popen(['node', server_path], env=my_env)

    try:
        # wait for the server to spin up
        time.sleep(1.0)
        az.ccg.reset_graph()
        az.analyze()
        # assert_graph_match_history(az)

        history_truth = {
            'C': {'main.js:funcB:9:12': 1,
                  'main.js:global': 1,
                  'main.js:main:7:16': 1},
            'B': {'main.js:funcB:9:11': 3,
                  'main.js:global': 7,
                  'main.js:main:7:15': 7},
            'A': {'main.js:funcA:3:5': 3,
                  'main.js:main:7:10': 4,
                  'main.js:global': 12}
        }

        for commit in az.ri.repo.iter_commits():
            assert(az.history[commit.hexsha] ==
                   history_truth[commit.message.strip()])

        edges_truth = [
            ('main.js:funcB:9:12', 'Native:Window_prototype_print'),
            ('main.js:funcB:9:12', 'main.js:funcA:3:5'),
            ('main.js:funcA:3:5', 'Native:Window_prototype_print'),
            ('main.js:main:7:16', 'main.js:funcB:9:12'),
            ('main.js:main:7:16', 'main.js:funcA:3:5'),
            ('main.js:global', 'main.js:main:7:16')
        ]
        assert(set(az.ccg.get_graph().edges()) == set(edges_truth))

    finally:
        proc.terminate()
