import os
import pytest
import subprocess
import shutil
from persper.analytics.cpp import CPPGraphServer
from persper.analytics.analyzer2 import Analyzer
from persper.analytics.graph_server import CPP_FILENAME_REGEXES
from persper.util.path import root_path

@pytest.fixture(scope='module')
def az():
    # build the repo first if not exists yet
    repo_path = os.path.join(root_path, 'repos/cpp_test_files_repo')
    script_path = os.path.join(root_path, 'tools/repo_creater/create_repo.py')
    test_src_path = os.path.join(root_path, 'test/cpp_test_files_repo')

    # Always use latest source to create test repo
    if os.path.exists(repo_path):
        shutil.rmtree(repo_path)

    cmd = '{} {}'.format(script_path, test_src_path)
    subprocess.call(cmd, shell=True)

    return Analyzer(repo_path, CPPGraphServer(CPP_FILENAME_REGEXES))


@pytest.mark.asyncio
async def test_analyzer_files(az):
    az.terminalCommit = 'A'
    await az.analyze()
    assert az.graph.nodes(data=True)['main']['files'] == set(['main.cpp'])

    az.terminalCommit = 'B'
    await az.analyze()
    assert az.graph.nodes(data=True)['main']['files'] == set(['main_renamed.cpp'])

    az.terminalCommit = 'C'
    await az.analyze()
    assert az.graph.nodes(data=True)['main']['files'] == set(['main_renamed.cpp', 'another_main.cpp'])
    ccgraph = az.graph

    history_truth = {
        'C': {
            'printmessage': {'adds': 4, 'dels': 0},
            'main': {'adds': 4, 'dels': 0}
        },
        'B': {},
        'A': {
            'addition': {'adds': 6, 'dels': 0},
            'main': {'adds': 6, 'dels': 0}
        },
    }

    commits = ccgraph.commits()
    for func, data in ccgraph.nodes(data=True):
        history = data['history']

        for cid, chist in history.items():
            message = commits[cid]['message']
            assert chist == history_truth[message.strip()][func]

    edges_truth = [
        ('main', 'addition'),
        ('main', 'printmessage')
    ]
    assert set(ccgraph.edges()) == set(edges_truth)
