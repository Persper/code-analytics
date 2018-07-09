import os
import pytest
from persper.graphs.js import JSGraph
from persper.graphs.analyzer import Analyzer
from persper.util.path import root_path


def test_map_id():
    repo_path = os.path.join(root_path, 'repos/js_test_repo')
    script_path = os.path.join(root_path, 'tools/repo_creater/create_repo.py')
    test_src_path = os.path.join(root_path, 'test/js_test_repo')
    if not os.path.isdir(repo_path):
        cmd = '{} {}'.format(script_path, test_src_path)
        subprocess.call(cmd, shell=True)

    server_addr = 'http://localhost:3000'
    az = Analyzer(repo_path, JSGraph(server_addr))

    az.ordered_shas = ['c1', 'c2', 'c3', 'c4', 'c5', 'c6', 'c7']

    az.id_map = {
        'c1': {'A': 'B'},
        'c2': {'B': 'C', 'E': 'F'},
        'c3': {'C': 'D', 'F': 'G'},
        'c4': {'G': 'H'},
        'c5': {'D': 'I', 'J': 'K'},
        'c6': {'I': 'B', 'H': 'E'},  # make two cycles
        'c7': {'B': 'L'}  # remove a cycle
    }

    final_map_truth = {
        'A': 'L',
        'B': 'L',
        'C': 'L',
        'D': 'L',
        'I': 'L',
        'E': 'E',
        'F': 'E',
        'G': 'E',
        'H': 'E',
        'J': 'K'
    }

    final_map = az.aggregate_id_map()
    assert(final_map_truth == final_map)
