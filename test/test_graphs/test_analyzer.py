import os
import pytest
import pickle
import subprocess
from persper.graphs.c import CGraph
from persper.graphs.analyzer import Analyzer
from persper.graphs.iterator import RepoIterator
from persper.util.path import root_path


@pytest.fixture(scope='module')
def az():
    # build the repo first if not exists yet
    repo_path = os.path.join(root_path, 'repos/test_feature_branch')
    script_path = os.path.join(root_path, 'tools/repo_creater/create_repo.py')
    test_src_path = os.path.join(root_path, 'test/test_feature_branch')
    if not os.path.isdir(repo_path):
        cmd = '{} {}'.format(script_path, test_src_path)
        subprocess.call(cmd, shell=True)

    return Analyzer(repo_path, CGraph())


def test_az_basic(az):
    # calling analyze twice should make no differenece
    az.analyze(from_beginning=True, into_branches=True)
    az.analyze(from_beginning=True, into_branches=True)

    history_truth = {
        'J': {'count': 12, 'display': 14},
        'I': {'add': 5, 'append': 35, 'insert': 25},
        'E': {},
        'G': {'str_equals': 1, 'str_replace': 26},
        'D': {},
        'H': {'add': 16, 'append': 12, 'insert': 25},
        'F': {},
        'A': {'str_append': 7, 'str_len': 6},
        'K': {'display': 5},
        'C': {'str_append_chr': 34, 'str_equals': 1},
        'B': {'str_append': 9, 'str_append_chr': 7, 'str_equals': 11}
    }

    for commit in az.ri.repo.iter_commits():
        assert(az.history[commit.hexsha] ==
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
    assert(set(az.ccg.get_graph().edges()) == set(edges_truth))


def assert_graphs_equal(G1, G2):
    assert(set(G1.nodes()) == set(G2.nodes()))
    assert(set(G1.edges()) == set(G2.edges()))
    for n in G1:
        print(n)
        assert(G1.node[n] == G2.node[n])


def assert_analyzer_equal(az1, az2):
    assert(az1.history == az2.history)
    assert_graphs_equal(az1.ccg.get_graph(), az2.ccg.get_graph())


def test_analyze_interface(az):
    """test various ways to invoke process function"""
    az.analyze(from_beginning=True, into_branches=True)

    repo_path = os.path.join(root_path, 'repos/test_feature_branch')
    az1 = Analyzer(repo_path, CGraph())
    # A B
    az1.analyze(from_beginning=True, num_commits=2, into_branches=True)
    # C D
    az1.analyze(continue_iter=True, num_commits=2, into_branches=True)
    # E F K
    az1.analyze(continue_iter=True, num_commits=3, into_branches=True)
    # should see "The range specified is empty, terminated."
    az1.analyze(continue_iter=True, num_commits=1, into_branches=True)
    assert_analyzer_equal(az1, az)

    az2 = Analyzer(repo_path, CGraph())
    ri = RepoIterator(repo_path)
    commits, _ = ri.iter(from_beginning=True)
    assert(len(commits) == 7)
    # should see "No history exists yet, terminated."
    az2.analyze(continue_iter=True, num_commits=1, into_branches=True)
    # A B C
    az2.analyze(from_beginning=True, num_commits=3, into_branches=True)
    # D E F
    az2.analyze(from_beginning=True,
                end_commit_sha=commits[5].hexsha,
                into_branches=True)
    # K
    az2.analyze(from_beginning=True,
                end_commit_sha=commits[6].hexsha,
                into_branches=True)
    assert_analyzer_equal(az2, az)


def test_save(az):
    az.analyze(from_beginning=True, into_branches=True)
    fname = "test_save_g.pickle"
    az.save(fname)
    with open(fname, 'rb') as f:
        az1 = pickle.load(f)
    os.remove(fname)
    assert_analyzer_equal(az, az1)
