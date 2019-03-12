import os
import pytest
import subprocess
import shutil
from persper.analytics.java import JavaGraphServer
from persper.analytics.analyzer import Analyzer
from persper.analytics.graph_server import JAVA_FILENAME_REGEXES
from persper.util.path import root_path


@pytest.fixture(scope='module')
def az():
    # build the repo first if not exists yet
    repo_path = os.path.join(root_path, 'repos/java_test_repo')
    script_path = os.path.join(root_path, 'tools/repo_creater/create_repo.py')
    test_src_path = os.path.join(root_path, 'test/java_test_repo')

    # Always use latest source to create test repo
    if os.path.exists(repo_path):
        shutil.rmtree(repo_path)

    cmd = '{} {}'.format(script_path, test_src_path)
    subprocess.call(cmd, shell=True)

    return Analyzer(repo_path, JavaGraphServer(JAVA_FILENAME_REGEXES))


@pytest.mark.asyncio
async def test_analyzer_master_only(az):
    await az.analyze(from_beginning=True)
    ccgraph = az.get_graph()

    history_truth = {
        'A': {
            'main': {'adds': 3, 'dels': 0},
            'doStuff': {'adds': 3, 'dels': 0},
            'addFunction': {'adds': 4, 'dels': 0}
        },
        'B': {
            'addFunction': {'adds': 4, 'dels': 0},
            'tempFunction': {'adds': 3, 'dels': 0}
        },
        'C': {
            'tempFunction': {'adds': 0, 'dels': 3}
        },
        'D': {
            'addFunction': {'adds': 1, 'dels': 1},
            'AddChangeFunction': {'adds': 1, 'dels': 0}
        },
        'E': {
            'AddChangeFunction': {'adds': 2, 'dels': 2}
        },
        'F': {
            'AddChangeFunction': {'adds': 4, 'dels': 0}
        },
        'G': {
            'AddChangeFunction': {'adds': 0, 'dels': 2}
        },
        'I': {
            'AddChangeFunction': {'adds': 3, 'dels': 3}
        },
        'J': {
            'AddChangeFunction': {'adds': 1, 'dels': 1},
            'doStuff': {'adds': 0, 'dels': 1}
        },
        'K': {
            'AddChangeFunction': {'adds': 0, 'dels': 2},
            'FunctionCaller': {'adds': 5, 'dels': 0},
            'doStuff': {'adds': 3, 'dels': 1}
        }
    }

    edges_truth = [
        ('doStuff', 'newA().foo()'),
        ('FunctionCaller', 'summation')
    ]

    commits = ccgraph.commits()

    for func, data in ccgraph.nodes(data=True):
        history = data['history']

        for cid, chist in history.items():
            message = commits[cid]['message']
            # print(message.strip(), chist, func.strip())
            assert (chist == history_truth[message.strip()][func])

    filenames = list()
    filenames_truth = ['CallGraph.java']
    for func, data in ccgraph.nodes(data=True):
        filenames.extend(data["files"])
    assert (set(filenames) == set(filenames_truth))

    # print(az._graph_server.get_graph().edges())
    assert (set(az._graph_server.get_graph().edges()) == set(edges_truth))
