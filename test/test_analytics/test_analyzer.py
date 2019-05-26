import os
import pytest
import subprocess
import shutil
from persper.analytics.c import CGraphServer
from persper.analytics.analyzer import Analyzer
from persper.analytics.graph_server import C_FILENAME_REGEXES
from persper.util.path import root_path


@pytest.fixture(scope='module')
def az():
    # build the repo first if not exists yet
    repo_path = os.path.join(root_path, 'repos/test_feature_branch')
    script_path = os.path.join(root_path, 'tools/repo_creater/create_repo.py')
    test_src_path = os.path.join(root_path, 'test/test_feature_branch')

    # Always use latest source to create test repo
    if os.path.exists(repo_path):
        shutil.rmtree(repo_path)

    cmd = '{} {}'.format(script_path, test_src_path)
    subprocess.call(cmd, shell=True)

    return Analyzer(repo_path, CGraphServer(C_FILENAME_REGEXES))


@pytest.mark.asyncio
async def test_analyzer_master_only(az):
    await az.analyze(from_beginning=True)
    ccgraph = az.get_graph()

    history_truth = {
        'K': {
            'display': {'adds': 0, 'dels': 5, 'added_units': 0, 'removed_units': 10}
        },
        'F': {
            'display': {'adds': 14, 'dels': 0, 'added_units': 23, 'removed_units': 0},
            'count': {'adds': 12, 'dels': 0, 'added_units': 19, 'removed_units': 0}
        },
        'E': {
            'append': {'adds': 29, 'dels': 0, 'added_units': 44, 'removed_units': 0},
            'add': {'adds': 11, 'dels': 0, 'added_units': 25, 'removed_units': 0}
        },
        'D': {
            'str_replace': {'adds': 26, 'dels': 0, 'added_units': 76, 'removed_units': 0}
        },
        # TODO: fix \No newline at the end of file
        'C': {
            'str_append_chr': {'adds': 30, 'dels': 4, 'added_units': 78, 'removed_units': 21},
            'str_equals': {'adds': 0, 'dels': 1, 'added_units': 0, 'removed_units': 0}
        },
        # Commit `B` is an example of imperfect diff,
        # it removes `str_append` and adds a new function `str_append_chr`
        # but because they are too similar,
        # diff doesn't separate these changes into two chunks
        # please see here: https://github.com/UltimateBeaver/test_feature_branch/commit/caaac10f604ea7ac759c2147df8fb2b588ee2a27
        'B': {
            'str_append': {'adds': 6, 'dels': 3, 'added_units': 29, 'removed_units': 21},
            'str_append_chr': {'adds': 3, 'dels': 2, 'added_units': 21, 'removed_units': 15},
            'str_equals': {'adds': 11, 'dels': 0, 'added_units': 27, 'removed_units': 0}
        },
        'A': {
            'str_append': {'adds': 7, 'dels': 0, 'added_units': 29, 'removed_units': 0},
            'str_len': {'adds': 6, 'dels': 0, 'added_units': 13, 'removed_units': 0}
        },


        # # branch J from commit A, merge back through F
        # 'J': {
        #     'count': {'adds': 12, 'dels': 0},
        #     'display': {'adds': 14, 'dels': 0}
        # },

        # # TODO: fix \No newline at the end of file
        # # branch G from commit B, merge back through D
        # 'G': {
        #     'str_equals': {'adds': 0, 'dels': 1},
        #     'str_replace': {'adds': 26, 'dels': 0}
        # },

        # # branch H from commit D, merge back through  E
        # 'H': {
        #     'add': {'adds': 16, 'dels': 0},
        #     'append': {'adds': 12, 'dels': 0},
        #     'insert': {'adds': 25, 'dels': 0}
        # },
        # 'I': {
        #     'add': {'adds': 0, 'dels': 5},
        #     'append': {'adds': 26, 'dels': 9},
        #     'insert': {'adds': 0, 'dels': 25}
        # },
    }

    commits = ccgraph.commits()
    for func, data in ccgraph.nodes(data=True):
        history = data['history']

        for cid, chist in history.items():
            message = commits[cid]['message']
            assert chist == history_truth[message.strip()][func]

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
    assert set(az._graph_server.get_graph().edges()) == set(edges_truth)
