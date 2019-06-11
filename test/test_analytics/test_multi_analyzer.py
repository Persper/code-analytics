import os
import pytest
from git import Repo
from persper.analytics.multi_analyzer import MultiAnalyzer
from persper.util.path import root_path


@pytest.fixture(scope='module')
def vue_repo_path():
    repo_path = os.path.join(root_path, "repos/vue-realworld-example-app")
    repo_url = 'https://github.com/gothinkster/vue-realworld-example-app'
    if not os.path.exists(repo_path):
        Repo.clone_from(repo_url, repo_path)
    return repo_path


@pytest.fixture(scope='module')
def ts_repo_path():
    repo_path = os.path.join(root_path, "repos/TypeScriptSamples")
    repo_url = 'https://github.com/microsoft/TypeScriptSamples'
    if not os.path.exists(repo_path):
        Repo.clone_from(repo_url, repo_path)
    return repo_path


def test_set_linguist_vue(vue_repo_path):
    # _set_linguist is called during the initialization of MultiAnalyzer
    maz = MultiAnalyzer(vue_repo_path)


def test_set_linguist_ts(ts_repo_path):
    # _set_linguist is called during the initialization of MultiAnalyzer
    maz = MultiAnalyzer(ts_repo_path)
