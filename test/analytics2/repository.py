import os.path
import subprocess
from test.analytics2.abstractions.repository import \
    test_repository_history_provider

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
    repo = GitRepository(repoPath)
    test_repository_history_provider(repo)
