import os
import pytest
import subprocess
import shutil
from persper.analytics.java import JavaGraphServer
from persper.analytics.analyzer2 import Analyzer
from persper.analytics.graph_server import JAVA_FILENAME_REGEXES
from persper.util.path import root_path


@pytest.fixture(scope='module')
def az():
    # build the repo first if not exists yet
    repo_path = os.path.join(root_path, 'repos/java_test_repo')
    script_path = os.path.join(root_path, 'tools/repo_creater/create_repo.py')
    test_src_path = os.path.join(root_path, 'test/java_test_repo')

    # Always use latest source to create test repo
    if os.path.exists(repo_path):
        shutil.rmtree(repo_path)

    cmd = '{} {}'.format(script_path, test_src_path)
    subprocess.call(cmd, shell=True)

    return Analyzer(repo_path, JavaGraphServer(JAVA_FILENAME_REGEXES))


@pytest.mark.asyncio
async def test_analyzer_master_only(az):
    await az.analyze()
    ccgraph = az.graph

    history_truth = {
        'A': {
            'main': {'adds': 3, 'dels': 0},
            'doStuff': {'adds': 3, 'dels': 0},
            'addFunction': {'adds': 4, 'dels': 0}
        },
        'B': {
            'tempFunction': {'adds': 3, 'dels': 0}
        },
        'C': {
            'tempFunction': {'adds': 0, 'dels': 3}
        },
        'D': {
            'addFunction': {'adds': 1, 'dels': 1},
            'AddChangeFunction': {'adds': 1, 'dels': 0}
        },
        'E': {
            'AddChangeFunction': {'adds': 2, 'dels': 2}
        },
        'F': {
            'AddChangeFunction': {'adds': 4, 'dels': 0}
        },
        'G': {
            'AddChangeFunction': {'adds': 0, 'dels': 2}
        },
        'I': {
            'AddChangeFunction': {'adds': 3, 'dels': 3}
        },
        'J': {
            'AddChangeFunction': {'adds': 1, 'dels': 1},
            'doStuff': {'adds': 0, 'dels': 1}
        },
        'K': {
            'AddChangeFunction': {'adds': 3, 'dels': 1},
            'FunctionCaller': {'adds': 5, 'dels': 0},
            'doStuff': {'adds': 0, 'dels': 1}
        },
        'L': {
            'FunctionCaller': {'adds': 3, 'dels': 2},
            'AddChangeFunction': {'adds': 0, 'dels': 1}
        },
        'M': {
            'FunctionCaller': {'adds': 0, 'dels': 3}
        },
        'N': {
            'FunctionCaller': {'adds': 3, 'dels': 0}
        },
        'O': {
            'FunctionCallerConditionals': {'adds': 10, 'dels': 0},
            'FunctionCallerConditionalsSwitch': {'adds': 33, 'dels': 0}
        },
        'P': {
            'FunctionCallerLoops': {'adds': 10, 'dels': 0}
        },
        # New file added having same function name
        'Q': {
            'main': {'adds': 3, 'dels': 0},
            'doStuff': {'adds': 3, 'dels': 0}
        }

    }

    edges_truth = [
        ('doStuff', 'newA().foo()'),
        # caller callee relationship
        ('FunctionCaller', 'summation'),
        # modifying function call
        ('FunctionCaller', 'summation_new'),
        # Statement expressions
        ('FunctionCaller', 'addMore'),
        ('FunctionCaller', 'addNewNumber'),
        # Embedded functions
        ('FunctionCaller', 'add40'),
        ('FunctionCaller', 'returnBigValues'),
        ('FunctionCaller', 'sumValue'),
        ('FunctionCaller', 'anotherValue'),
        # If conditionals
        ('FunctionCallerConditionals', 'addMoreAgain'),
        ('FunctionCallerConditionals', 'greater30'),
        ('FunctionCallerConditionals', 'anotherValueAgain'),
        # Switch Test
        ('FunctionCallerConditionalsSwitch', 'getDay'),
        ('FunctionCallerConditionalsSwitch', 'getNumDay'),
        # Loops
        ('FunctionCallerLoops', 'getValue'),
        ('FunctionCallerLoops', 'length'),
        ('FunctionCallerLoops', 'doSomething'),
        ('FunctionCallerLoops', 'doSomthingMore'),
        ('FunctionCallerLoops', 'parseIt'),
        # New file with same function name
        ('doStuff', 'callSum')
    ]

    commits = ccgraph.commits()

    for func, data in ccgraph.nodes(data=True):
        history = data['history']

        for cid, chist in history.items():
            message = commits[cid]['message']
            print(message.strip(), chist, func.strip())
            assert (chist == history_truth[message.strip()][func])

    filenames = list()
    filenames_truth = ['CallGraph.java', 'SecondFile.java', 'SecondFileRename.java']
    for func, data in ccgraph.nodes(data=True):
        filenames.extend(data["files"])
    assert (set(filenames) == set(filenames_truth))

    print(az.graph.edges())
    assert (set(az.graph.edges()) == set(edges_truth))
