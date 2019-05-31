import os
import pytest
from git import Repo
from persper.analytics.multi_analyzer import MultiAnalyzer
from persper.util.path import root_path


@pytest.fixture(scope='module')
def repo_path():
    repo_path = os.path.join(root_path, "repos/vue-realworld-example-app")
    repo_url = 'https://github.com/gothinkster/vue-realworld-example-app'
    if not os.path.exists(repo_path):
        Repo.clone_from(repo_url, repo_path)
    return repo_path


def test_set_linguist(repo_path):
    maz = MultiAnalyzer(repo_path)
