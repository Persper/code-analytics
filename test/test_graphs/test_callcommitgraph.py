import os
import pytest
import pickle
import subprocess
from persper.graphs.call_commit_graph import CallCommitGraph
from persper.graphs.call_commit_graph import _inverse_diff_result
from persper.util.path import root_path


@pytest.fixture(scope='module')
def g():
    # build the repo first if not exists yet
    repo_path = os.path.join(root_path, 'repos/test_feature_branch')
    script_path = os.path.join(root_path, 'tools/repo_creater/create_repo.py')
    test_src_path = os.path.join(root_path, 'test/test_feature_branch')
    if not os.path.isdir(repo_path):
        cmd = '{} {}'.format(script_path, test_src_path)
        subprocess.call(cmd, shell=True)

    g = CallCommitGraph(repo_path)
    g.process(from_beginning=True, verbose=True, into_branches=True)
    return g


def test_callcommitgraph(g):
    history_truth = {
        'J': {'count': 12, 'display': 14},
        'I': {'add': 5, 'append': 35},
        'E': {},
        'G': {'str_equals': 1, 'str_replace': 26},
        'D': {},
        'H': {'add': 16, 'append': 12},
        'F': {},
        'A': {'str_append': 7, 'str_len': 6},
        'K': {'display': 5},
        'C': {'str_append_chr': 34, 'str_equals': 1},
        'B': {'str_append': 9, 'str_append_chr': 7, 'str_equals': 11}
    }

    for commit in g.repo.iter_commits():
        assert(g.history[commit.hexsha] ==
               history_truth[commit.message.strip()])

    edges_truth = [
        ('append', 'free'),
        ('display', 'printf'),
        ('str_replace', 'str_append_chr'),
        ('str_replace', 'str_equals'),
        ('str_replace', 'str_len'),
        ('str_replace', 'str_append'),
        ('str_append_chr', 'str_append_chr'),
        ('str_append_chr', 'str_equals'),
        ('str_append_chr', 'str_len'),
        ('str_append_chr', 'str_append'),
        ('add', 'malloc')
    ]
    assert(set(g.G.edges()) == set(edges_truth))


def test_inverse_diff():
    # view parsing ground truth here
    # https://github.com/basicthinker/Sexain-MemController/commit/f050c6f6dd4b1d3626574b0d23bb41125f7b75ca
    adds_dels = (
        [[7, 31], [27, 3], [44, 1], [50, 2], [70, 1], [77, 2], [99, 2]],
        [[32, 44], [56, 70]]
    )
    inv_truth = (
        [[65, 13], [79, 15]],
        [[8, 38], [59, 61], [66, 66], [73, 74], [80, 80], [88, 89], [112, 113]]
    )

    inv_result = _inverse_diff_result(*adds_dels)
    assert(inv_truth == inv_result)


def assert_graphs_equal(G1, G2):
    assert(set(G1.nodes()) == set(G2.nodes()))
    assert(set(G1.edges()) == set(G2.edges()))
    for n in G1:
        assert(G1.node[n] == G2.node[n])


def assert_callcommitgraphs_equal(g1, g2):
    assert_graphs_equal(g1.G, g2.G)
    assert(g1.history == g2.history)
    assert(g1.exts == g2.exts)


def test_process_interface(g):
    """test various ways to invoke process function"""
    repo_path = os.path.join(root_path, 'repos/test_feature_branch')
    g1 = CallCommitGraph(repo_path)
    # A B
    g1.process(from_beginning=True, into_branches=True, num_commits=2)
    # C D
    g1.process(from_last_processed=True, into_branches=True, num_commits=2)
    # E F K
    g1.process(from_last_processed=True, into_branches=True, num_commits=3)
    # should see "The range specified is empty, terminated."
    g1.process(from_last_processed=True, into_branches=True, num_commits=1)
    assert_callcommitgraphs_equal(g1, g)

    g2 = CallCommitGraph(repo_path)
    # should see "No history exists yet, terminated."
    g2.process(from_last_processed=True, into_branches=True, num_commits=1)
    # A B C
    g2.process(from_beginning=True, into_branches=True, num_commits=3)
    # D E F
    g2.process(from_beginning=True,
               into_branches=True,
               end_commit_sha=g.commits[5].hexsha)
    # K
    g2.process(from_beginning=True,
               into_branches=True,
               end_commit_sha=g.commits[6].hexsha)
    assert_callcommitgraphs_equal(g2, g)


def test_save(g):
    fname = "test_save_g.pickle"
    g.save(fname)
    with open(fname, 'rb') as f:
        gp = pickle.load(f)
    os.remove(fname)
    assert_callcommitgraphs_equal(g, gp)
