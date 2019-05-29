import os
import pytest
import subprocess
import shutil
from persper.analytics.c import CGraphServer
from persper.analytics.analyzer2 import Analyzer
from persper.analytics.graph_server import C_FILENAME_REGEXES, CommitSeekingMode
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


def test_analyzer_filter_monolithic_commit(az):
    threshold = az._monolithic_commit_lines_threshold

    # case 1: changes above threshold, but the commit is the first commit
    # expected result: normal forward
    case_1_files = {
        'main.c': {'lines': threshold + 1},
    }
    case_1_commit = MockCommit(case_1_files, 0)
    case_1_seeking_mode = az._filter_monolithic_commit(case_1_commit, CommitSeekingMode.NormalForward)
    assert case_1_seeking_mode == CommitSeekingMode.NormalForward

    # case 2: changes equal to threshold, the commit has one parent commit
    # expected result: normal forward
    case_2_files = {
        'a.c': {'lines': threshold},
    }
    case_2_commit = MockCommit(case_2_files, 1)
    case_2_seeking_mode = az._filter_monolithic_commit(case_2_commit, CommitSeekingMode.NormalForward)
    assert case_2_seeking_mode == CommitSeekingMode.NormalForward

    # case 3: changes above threshold, the commit has one parent commit
    # expected result: merge commit
    case_3_files = {
        'a.c': {'lines': threshold},
        'b.c': {'lines': 1},
    }
    case_3_commit = MockCommit(case_3_files, 1)
    case_3_seeking_mode = az._filter_monolithic_commit(case_3_commit, CommitSeekingMode.NormalForward)
    assert case_3_seeking_mode == CommitSeekingMode.MergeCommit

    # case 4: changes equal to threshold, the commit is a merge commit
    # expected result: merge commit
    case_4_files = {
        'a.c': {'lines': threshold},
    }
    case_4_commit = MockCommit(case_4_files, 2)
    case_4_seeking_mode = az._filter_monolithic_commit(case_4_commit, CommitSeekingMode.MergeCommit)
    assert case_4_seeking_mode == CommitSeekingMode.MergeCommit


class MockCommit:
    def __init__(self, files: dict, parent_number: int = 1):
        self.hexsha = 'test'
        self.stats = MockCommitStats(files)
        self.parents = [{}] * parent_number


class MockCommitStats:
    def __init__(self, files: dict):
        self.files = files
