import os
import pytest
from git import Repo
from persper.analytics.git_tools import diff_with_first_parent, diff_with_commit
from persper.util.path import root_path


@pytest.fixture(scope='module')
def bitcoin_repo():
    repo_path = os.path.join(root_path, "repos/bitcoin")
    bitcoin_url = 'https://github.com/bitcoin/bitcoin'
    if not os.path.exists(repo_path):
        Repo.clone_from(bitcoin_url, repo_path)
    return Repo(repo_path)


def test_diff_ignore_space(bitcoin_repo):
    """
    bitcoin project has a commit which only converts CRLF to LF
    its diff with parent should be empty when
    ignore space option is enabled
    The CRLF commit: https://github.com/bitcoin/bitcoin/commit/0a61b0df1224a5470bcddab302bc199ca5a9e356
    """
    crlf_sha = '0a61b0df1224a5470bcddab302bc199ca5a9e356'
    crlf_commit = bitcoin_repo.commit(crlf_sha)
    diff_result = diff_with_first_parent(bitcoin_repo, crlf_commit)
    assert len(diff_result) == 0


def test_empty_current_commit(bitcoin_repo):
    """
    When rewinding to an orphaned commit, the `current_commit` passed to the `diff_with_commit` function is None.
    This test case makes sure we handle this scenario without throwing an `Exception`.
    `base_commit` is the first commit in the bitcoin repo, which adds 45 new files
    Link: https://github.com/bitcoin/bitcoin/commit/4405b78d6059e536c36974088a8ed4d9f0f29898
    """
    current_commit = None
    base_commit_sha = '4405b78d6059e536c36974088a8ed4d9f0f29898'
    diff_index = diff_with_commit(bitcoin_repo, current_commit, base_commit_sha)
    assert len(diff_index) == 45
