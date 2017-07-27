import os
import pytest
import pickle
import subprocess
from graphs.processor import Processor
from util.path import root_path


def setup_module(module):
    # build the repo first if not exists yet
    repo_path = os.path.join(root_path, 'repos/test_processor')
    script_path = os.path.join(root_path, 'repos/repo_creater/create_repo.py')
    test_src_path = os.path.join(root_path, 'test/test_processor')
    if not os.path.isdir(repo_path):
        cmd = '{} {}'.format(script_path, test_src_path)
        subprocess.call(cmd, shell=True)


def test_processor(capsys):
    repo_path = os.path.join(root_path, 'repos/test_processor')
    p = Processor(repo_path)
    p.process(from_beginning=True, into_branches=True)
    # from A to L
    assert(len(p.visited) == 12)
    out, _ = capsys.readouterr()
    assert("Commit No.6  Branch No.3" in out)
