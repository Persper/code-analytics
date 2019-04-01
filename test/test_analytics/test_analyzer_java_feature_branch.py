import os
import pytest
import subprocess
import shutil
from persper.analytics.java import JavaGraphServer
from persper.analytics.analyzer2 import Analyzer
from persper.analytics.graph_server import JAVA_FILENAME_REGEXES
from persper.util.path import root_path


@pytest.fixture(scope='module')
def az():
    # build the repo first if not exists yet
    repo_path = os.path.join(root_path, 'repos/java_test_feature_branch')
    script_path = os.path.join(root_path, 'tools/repo_creater/create_repo.py')
    test_src_path = os.path.join(root_path, 'test/java_test_feature_branch')

    # Always use latest source to create test repo
    if os.path.exists(repo_path):
        shutil.rmtree(repo_path)

    cmd = '{} {}'.format(script_path, test_src_path)
    subprocess.call(cmd, shell=True)

    return Analyzer(repo_path, JavaGraphServer(JAVA_FILENAME_REGEXES))


@pytest.mark.asyncio
async def test_analyzer_master_only(az):
    await az.analyze()
    ccgraph = az.graph

    history_truth = {
        'A': {
            'main': {'adds': 3, 'dels': 0},
            'addFunction': {'adds': 4, 'dels': 0},
            'doStuff': {'adds': 3, 'dels': 0},
        },
        'B': {
            'addNewFunction': {'adds': 4, 'dels': 0}
        },
        'C': {
            'addNewFunction': {'adds': 0, 'dels': 1}
        },
        'G': {
            'main': {'adds': 3, 'dels': 0},
            'doStuff': {'adds': 3, 'dels': 0},
            'addNewFunction': {'adds': 0, 'dels': 4}
        }

    }

    edges_truth = [
        ('addFunction', 'doStuff'),
        ('main', 'doStuff'),
        ('doStuff', 'foo'),
        ('doStuff', 'callSum'),
        ('addNewFunction', 'doNewStuff')
    ]

    commits = ccgraph.commits()

    for func, data in ccgraph.nodes(data=True):
        history = data['history']

        for cid, chist in history.items():
            message = commits[cid]['message']
            print(message.strip(), chist, func.strip())
            assert (chist == history_truth[message.strip()][func])

    filenames = list()
    filenames_truth = ['CallGraph.java', 'SecondFile.java']
    for func, data in ccgraph.nodes(data=True):
        filenames.extend(data["files"])
    assert (set(filenames) == set(filenames_truth))

    print(az.graph.edges())
    assert (set(az.graph.edges()) == set(edges_truth))
