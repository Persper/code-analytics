import os
import pytest
import pickle
import subprocess
from persper.analytics.iterator import RepoIterator
from persper.util.path import root_path


def serialized_messages(commits):
    return ' '.join([c.message.strip() for c in commits])


@pytest.fixture(scope='module')
def ri():
    # build the repo first if not exists yet
    repo_path = os.path.join(root_path, 'repos/test_processor')
    script_path = os.path.join(root_path, 'tools/repo_creater/create_repo.py')
    test_src_path = os.path.join(root_path, 'test/test_processor')
    if not os.path.isdir(repo_path):
        cmd = '{} {}'.format(script_path, test_src_path)
        subprocess.call(cmd, shell=True)

    repo_path = os.path.join(root_path, 'repos/test_processor')
    ri = RepoIterator(repo_path)
    return ri


def test_iterator(ri):
    commits, branch_commits = ri.iter(from_beginning=True, into_branches=True)
    # from A to L
    # use `git log --graph` to view ground truth
    assert(len(ri.visited) == 12)
    assert(len(commits) == 4)
    assert(len(branch_commits) == 8)
    assert(serialized_messages(commits) == 'D C B A')
    assert(serialized_messages(branch_commits) == 'G F E J I H L K')


def test_continue_iter(ri):
    commits, branch_commits = ri.iter(
        from_beginning=True, num_commits=2, into_branches=True)
    assert(serialized_messages(commits) == 'B A')
    assert(serialized_messages(branch_commits) == '')
    commits2, branch_commits2 = ri.iter(
        continue_iter=True, num_commits=2, into_branches=True)
    assert(serialized_messages(commits2) == 'D C')
    assert(serialized_messages(branch_commits2) == 'G F E J I H L K')


def test_rev(ri):
    commits, branch_commits = ri.iter(rev='C', into_branches=True)
    assert(serialized_messages(commits) == 'C B A')
    assert(serialized_messages(branch_commits) == '')
    commits2, branch_commits2 = ri.iter(
        continue_iter=True, end_commit_sha='D', into_branches=True)
    assert(serialized_messages(commits2) == 'D')
    assert(serialized_messages(branch_commits2) == 'G F E J I H L K')


def test_iter_twice(ri):
    commits, branch_commits = ri.iter(from_beginning=True, into_branches=True)
    commits2, branch_commits2 = ri.iter(
        from_beginning=True, into_branches=True)
    assert(commits == commits2)
    assert(branch_commits == branch_commits2)
