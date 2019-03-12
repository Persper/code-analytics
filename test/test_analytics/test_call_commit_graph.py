import os
import pytest
import shutil
import subprocess
from math import isclose
from git import Repo
from persper.analytics.call_commit_graph import CallCommitGraph
from persper.analytics.cpp import CPPGraphServer
from persper.analytics.analyzer import Analyzer
from persper.analytics.graph_server import CPP_FILENAME_REGEXES
from persper.util.path import root_path


def test_call_commit_graph():
    ccgraph = CallCommitGraph()
    first_commit = {
        'hexsha': '0x01',
        'authorName': 'koala',
        'authorEmail': 'koala@persper.org',
        'message': 'first commit'
    }
    ccgraph.add_commit(first_commit['hexsha'],
                       first_commit['authorName'],
                       first_commit['authorEmail'],
                       first_commit['message'])
    ccgraph.add_node('f1')
    ccgraph.update_node_history('f1', 10, 0)
    ccgraph.add_node('f2')
    ccgraph.update_node_history('f2', 10, 0)
    ccgraph.add_edge('f1', 'f2')

    func_drs = ccgraph.function_devranks(0.85)
    commit_drs = ccgraph.commit_devranks(0.85)
    dev_drs = ccgraph.developer_devranks(0.85)
    assert isclose(func_drs['f1'], 0.35, rel_tol=1e-2)
    assert isclose(func_drs['f2'], 0.65, rel_tol=1e-2)
    assert isclose(commit_drs[first_commit['hexsha']], 1)
    assert isclose(dev_drs[first_commit['authorEmail']], 1)

    second_commit = {
        'hexsha': '0x02',
        'authorName': 'beaver',
        'authorEmail': 'beaver@perpser.org',
        'message': 'second commit'
    }
    ccgraph.add_commit(second_commit['hexsha'],
                       second_commit['authorName'],
                       second_commit['authorEmail'],
                       second_commit['message'])
    ccgraph.add_node('f3')
    ccgraph.update_node_history('f3', 10, 0)
    ccgraph.add_edge('f1', 'f3')

    func_drs2 = ccgraph.function_devranks(0.85)
    commit_drs2 = ccgraph.commit_devranks(0.85)
    dev_drs2 = ccgraph.developer_devranks(0.85)
    assert isclose(func_drs2['f1'], 0.26, rel_tol=1e-2)
    assert isclose(func_drs2['f2'], 0.37, rel_tol=1e-2)
    assert isclose(func_drs2['f3'], 0.37, rel_tol=1e-2)
    assert isclose(commit_drs2[first_commit['hexsha']], 0.63, rel_tol=1e-2)
    assert isclose(commit_drs2[second_commit['hexsha']], 0.37, rel_tol=1e-2)
    assert isclose(dev_drs2[first_commit['authorEmail']], 0.63, rel_tol=1e-2)
    assert isclose(dev_drs2[second_commit['authorEmail']], 0.37, rel_tol=1e-2)

    third_commit = {
        'hexsha': '0x03',
        'authorName': 'koala',
        'authorEmail': 'koala@persper.org',
        'message': 'third commit'
    }
    ccgraph.add_commit(third_commit['hexsha'],
                       third_commit['authorName'],
                       third_commit['authorEmail'],
                       third_commit['message'])
    ccgraph.add_node('f4')
    ccgraph.update_node_history('f4', 10, 0)
    ccgraph.add_edge('f2', 'f4')

    ccgraph.add_node('f5')
    ccgraph.update_node_history('f5', 10, 0)
    ccgraph.add_edge('f2', 'f5')

    func_drs3 = ccgraph.function_devranks(0.85)
    commit_drs3 = ccgraph.commit_devranks(0.85)
    dev_drs3 = ccgraph.developer_devranks(0.85)
    assert isclose(func_drs3['f1'], 0.141, rel_tol=1e-2)
    assert isclose(func_drs3['f2'], 0.201, rel_tol=1e-2)
    assert isclose(func_drs3['f3'], 0.201, rel_tol=1e-2)
    assert isclose(func_drs3['f4'], 0.227, rel_tol=1e-2)
    assert isclose(func_drs3['f5'], 0.227, rel_tol=1e-2)
    assert isclose(commit_drs3[first_commit['hexsha']], 0.343, rel_tol=1e-2)
    assert isclose(commit_drs3[second_commit['hexsha']], 0.201, rel_tol=1e-2)
    assert isclose(commit_drs3[third_commit['hexsha']], 0.454, rel_tol=1e-2)
    assert isclose(dev_drs3[first_commit['authorEmail']], 0.798, rel_tol=1e-2)
    assert isclose(dev_drs3[second_commit['authorEmail']], 0.201, rel_tol=1e-2)


@pytest.mark.asyncio
async def test_black_set():
    """
    The CRLF commit: https://github.com/bitcoin/bitcoin/commit/0a61b0df1224a5470bcddab302bc199ca5a9e356
    Its parent: https://github.com/bitcoin/bitcoin/commit/5b721607b1057df4dfe97f80d235ed372312f398
    Its grandparent: https://github.com/bitcoin/bitcoin/commit/2ef9cfa5b81877b1023f2fcb82f5a638b1eb013c
    Its great grandparent: https://github.com/bitcoin/bitcoin/commit/7d7797b141dbd4ed9db1dda94684beb3395c2534
    Its great great grandparent: https://github.com/bitcoin/bitcoin/commit/401926283a200994ecd7df8eae8ced8e0b067c46
    """
    repo_path = os.path.join(root_path, 'repos/bitcoin')
    bitcoin_url = 'https://github.com/bitcoin/bitcoin'
    if not os.path.exists(repo_path):
        Repo.clone_from(bitcoin_url, repo_path)
    az = Analyzer(repo_path, CPPGraphServer(CPP_FILENAME_REGEXES))
    crlf_sha = '0a61b0df1224a5470bcddab302bc199ca5a9e356'
    parent_sha = '5b721607b1057df4dfe97f80d235ed372312f398'
    gggparent_sha = '401926283a200994ecd7df8eae8ced8e0b067c46'
    rev = gggparent_sha + '..' + crlf_sha
    await az.analyze(rev=rev)
    ccgraph = az.get_graph()
    devdict = ccgraph.commit_devranks(0.85)
    devdict2 = ccgraph.commit_devranks(0.85, black_set=set([parent_sha]))
    assert len(devdict) == 3
    assert len(devdict2) == 2
    assert parent_sha in devdict
    assert parent_sha not in devdict2
