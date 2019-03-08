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
            'main(String[]args)': {'adds': 4, 'dels': 0},
            'doStuff()': {'adds': 3, 'dels': 0}
        },
        'B': {
            'foo()': {'adds': 4, 'dels': 0},
            'bar()': {'adds': 3, 'dels': 0}
        }
    }
    commits = ccgraph.commits()

    for func, data in ccgraph.nodes(data=True):
        history = data['history']

        for cid, chist in history.items():
            message = commits[cid]['message']
            assert(chist == history_truth[message.strip()][func])
