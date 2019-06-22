import os
import pytest
import subprocess
import shutil
from git import Repo
from persper.util.path import root_path
from persper.analytics.git_tools import diff_with_first_parent, diff_with_commit



@pytest.fixture(scope='module')
def create_repo():
    # build the repo first if not exists yet
    repo_path = os.path.join(root_path, 'repos/git_test_ignore_all_space')
    script_path = os.path.join(root_path, 'tools/repo_creater/create_repo.py')
    test_src_path = os.path.join(root_path, 'test/git_test_ignore_all_space')

    # Always use latest source to create test repo
    if os.path.exists(repo_path):
        shutil.rmtree(repo_path)

    cmd = '{} {}'.format(script_path, test_src_path)
    subprocess.call(cmd, shell=True)
    return Repo(repo_path)


# @pytest.fixture(scope='module')
# def bitcoin_repo():
#     repo_path = os.path.join(root_path, "repos/bitcoin")
#     bitcoin_url = 'https://github.com/bitcoin/bitcoin'
#     if not os.path.exists(repo_path):
#         Repo.clone_from(bitcoin_url, repo_path)
#     return Repo(repo_path)


def test_diff_ignore_space(create_repo):
    """
    create new repo to test git diff --stat --ignore-all-space
    """

    commits = []
    for c in create_repo.iter_commits():
        commits.append(str(c))
    diff_result = diff_with_commit(commits[1], commits[0])
    diff = str(diff_result[0].diff) 
    diff = diff.replace("---", "")
    assert 48 == (diff.count("\n-")+diff.count("\n+"))
    

