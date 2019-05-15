import os.path
import subprocess
import test.analytics2.helpers.repository as repositoryhelper

from persper.analytics2.repository import GitRepository
from persper.util.path import root_path


def prepare_repository(repo_name: str):
    # build the repo first if not exists yet
    repo_path = os.path.join(root_path, 'repos/' + repo_name)
    script_path = os.path.join(root_path, 'tools/repo_creater/create_repo.py')
    test_src_path = os.path.join(root_path, 'test/' + repo_name)
    if not os.path.isdir(repo_path):
        cmd = '{} {}'.format(script_path, test_src_path)
        subprocess.call(cmd, shell=True)
    print("Repository path: ", repo_path)
    return repo_path


def test_git_repository():
    repoPath = prepare_repository("test_feature_branch")
    # TODO introduce some really complex repo, such as
    # repoPath = r"F:\WRS\testrepos\ccls"
    repo = GitRepository(repoPath)
    repositoryhelper.test_repository_history_provider(repo)
