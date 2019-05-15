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
