import os
import pytest
import subprocess
from persper.analytics.c import CGraphServer
from persper.analytics.analyzer import Analyzer
from persper.analytics.graph_server import C_FILENAME_REGEXES
from persper.util.path import root_path
from .util import assert_size_match_history


@pytest.fixture(scope='module')
def az():
    # build the repo first if not exists yet
    repo_path = os.path.join(root_path, 'repos/test_feature_branch')
    script_path = os.path.join(root_path, 'tools/repo_creater/create_repo.py')
    test_src_path = os.path.join(root_path, 'test/test_feature_branch')
    if not os.path.isdir(repo_path):
        cmd = '{} {}'.format(script_path, test_src_path)
        subprocess.call(cmd, shell=True)

    return Analyzer(repo_path, CGraphServer(C_FILENAME_REGEXES))


def test_az_basic(az):
    az.analyze(from_beginning=True)
    ccgraph = az.get_graph()

    history_truth = {
        'K': {'display': 5},
        'F': {'display': 14, 'count': 12},
        'E': {'append': 29, 'add': 11},
        'D': {'str_replace': 26},
        'C': {'str_append_chr': 34, 'str_equals': 1},
        # Commit 'B' adds function "str_append_chr" for 7 lines
        # Is it thought to be 5 lines because of inperfect diff
        'B': {'str_append': 9, 'str_append_chr': 5, 'str_equals': 11},
        'A': {'str_append': 7, 'str_len': 6},

        # branch J from commit A, merge back through F
        'J': {'count': 12, 'display': 14},

        # branch G from commit B, merge back through D
        'G': {'str_equals': 1, 'str_replace': 26},

        # branch H from commit D, merge back through  E
        'I': {'add': 5, 'append': 35, 'insert': 25},
        'H': {'add': 16, 'append': 12, 'insert': 25},
    }

    commits = ccgraph.commits()
    for func, data in ccgraph.nodes(data=True):
        size = data['size']
        history = data['history']
        assert_size_match_history(size, history)

        for cindex, csize in history.items():
            commit_message = commits[cindex]['message']
            assert(csize == history_truth[commit_message.strip()][func])

    edges_truth = [
        # Edges existing in final snapshot
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
        ('add', 'malloc'),
        # Edges existed in history
        ('str_append_chr', 'malloc'),
        ('str_append_chr', 'sprintf'),
        ('str_append', 'sprintf'),
        ('str_append', 'snprintf'),
        ('str_append_chr', 'snprintf'),
        ('str_append', 'malloc')
    ]
    assert(set(az._graph_server.get_graph().edges()) == set(edges_truth))
