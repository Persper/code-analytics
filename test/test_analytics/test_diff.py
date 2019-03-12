import os
from git import Repo
from persper.analytics.git_tools import diff_with_first_parent
from persper.util.path import root_path


def test_diff_ignore_space():
    """
    bitcoin project has a commit which only converts CRLF to LF
    its diff with parent should be empty when
    ignore space option is enabled
    The CRLF commit: https://github.com/bitcoin/bitcoin/commit/0a61b0df1224a5470bcddab302bc199ca5a9e356
    """
    repo_path = os.path.join(root_path, "repos/bitcoin")
    bitcoin_url = 'https://github.com/bitcoin/bitcoin'
    if not os.path.exists(repo_path):
        Repo.clone_from(bitcoin_url, repo_path)
    r = Repo(repo_path)
    crlf_sha = '0a61b0df1224a5470bcddab302bc199ca5a9e356'
    crlf_commit = r.commit(crlf_sha)
    diff_result = diff_with_first_parent(r, crlf_commit)
    assert len(diff_result) == 0
