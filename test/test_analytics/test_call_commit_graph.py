import os
import pytest
import shutil
import subprocess
from math import isclose
from git import Repo
from persper.analytics.call_commit_graph import CallCommitGraph
from persper.analytics.cpp import CPPGraphServer
from persper.analytics.analyzer import Analyzer
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

    assert ccgraph.eval_project_complexity() == 190
    assert ccgraph.eval_project_complexity(commit_black_list=set(['0x01'])) == 170


def test_devrank_with_accurate_history():
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
    ccgraph.update_node_history_accurate('f1', {'adds': 10, 'dels': 0, 'added_units': 20, 'removed_units': 0})
    ccgraph.add_node('f2')
    ccgraph.update_node_history_accurate('f2', {'adds': 10, 'dels': 0, 'added_units': 40, 'removed_units': 0})
    ccgraph.add_edge('f1', 'f2')

    func_drs = ccgraph.function_devranks(0.85)
    commit_drs = ccgraph.commit_devranks(0.85)
    dev_drs = ccgraph.developer_devranks(0.85)
    assert isclose(func_drs['f1'], 0.26, rel_tol=1e-2)
    assert isclose(func_drs['f2'], 0.74, rel_tol=1e-2)
    assert isclose(commit_drs[first_commit['hexsha']], 1)
    assert isclose(dev_drs[first_commit['authorEmail']], 1)


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
    az = Analyzer(repo_path, CPPGraphServer())
    crlf_sha = '0a61b0df1224a5470bcddab302bc199ca5a9e356'
    parent_sha = '5b721607b1057df4dfe97f80d235ed372312f398'
    gggparent_sha = '401926283a200994ecd7df8eae8ced8e0b067c46'
    rev = gggparent_sha + '..' + crlf_sha
    await az.analyze(rev=rev)
    ccgraph = az.get_graph()
    devdict = ccgraph.commit_devranks(0.85)
    devdict2 = ccgraph.commit_devranks(0.85, black_set=set([parent_sha]))
    print(devdict)
    print(devdict2)
    # CallCommitGraph.commit_devranks guarantee all commits to be present,
    # even if their devrank is 0 or they're present in the `black_set`
    assert devdict[parent_sha] > 0
    # commits that are in the `black_set` should now have zero devrank
    assert devdict2[parent_sha] == 0


def test_remove_invalid_nodes():
    ccgraph = CallCommitGraph()
    ccgraph.add_node('f1')
    ccgraph.add_node(None)
    ccgraph.add_edge('f1', None)

    func_drs = ccgraph.function_devranks(0.85)
    assert isclose(func_drs['f1'], 1, rel_tol=1e-2)


@pytest.fixture(scope='module')
def simple_ccg():
    ccgraph = CallCommitGraph()
    # add first commit with hexsha 0x01
    ccgraph.add_commit('0x01', None, None, None)
    ccgraph.add_node('f1')
    ccgraph.update_node_history_accurate('f1', {'adds': 10, 'dels': 0, 'added_units': 20, 'removed_units': 0})
    ccgraph.add_node('f2')
    ccgraph.update_node_history_accurate('f2', {'adds': 10, 'dels': 0, 'added_units': 40, 'removed_units': 0})
    ccgraph.add_edge('f1', 'f2')

    # add second commit with hexsha 0x02
    # this commit doesn't change source code
    ccgraph.add_commit('0x02', None, None, None)

    # add third commit with hexsha 0x03
    ccgraph.add_commit('0x03', None, None, None)
    ccgraph.add_node('f3')
    ccgraph.update_node_history_accurate('f3', {'adds': 5, 'dels': 0, 'added_units': 15, 'removed_units': 0})
    ccgraph.update_node_history_accurate('f2', {'adds': 3, 'dels': 3, 'added_units': 12, 'removed_units': 13})
    ccgraph.add_edge('f3', 'f2')
    return ccgraph


def test_get_commits_dev_eq(simple_ccg):
    # note that '0x02' is present in the ground truth
    assert {'0x01': 60, '0x02': 0, '0x03': 40} == simple_ccg.get_commits_dev_eq()


def test_commit_function_devranks(simple_ccg):
    commit_function_devranks_truth = {
        '0x01': {'f1': 0.15414381366361263, 'f2': 0.4493835852853403},
        '0x02': {},
        '0x03': {'f2': 0.2808647408033377, 'f3': 0.11560786024770947}
    }
    # verify the devranks in ground truth sum up to 1
    assert sum([sum(d.values()) for d in commit_function_devranks_truth.values()]) == 1.0
    assert commit_function_devranks_truth == simple_ccg.commit_function_devranks(0.85)
