import os
from graphs.call_commit_graph import CallCommitGraph, _inverse_diff_result

dir_path = os.path.dirname(os.path.abspath(__file__))

def get_parent_dir(path):
    return os.path.abspath(os.path.join(path, os.pardir))

def test_callcommitgraph():
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
    # build the repo first by running
    # `cd tools/repo_creater`
    # `./create_repo.py ../../test/test_feature_branch` 
    root_path = get_parent_dir(get_parent_dir(dir_path)) 
    g = CallCommitGraph(os.path.join(root_path, 'repos/test_feature_branch'))
    g.process(from_beginning=True, verbose=True, into_branches=True)
    for commit in g.repo.iter_commits():
        assert(g.history[commit.hexsha] == history_truth[commit.message.strip()])

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


