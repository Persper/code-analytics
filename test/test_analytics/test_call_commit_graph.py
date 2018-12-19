from math import isclose
from persper.analytics.call_commit_graph import CallCommitGraph


def test_call_commit_graph():
    ccgraph = CallCommitGraph()
    first_commit = {
        'hexsha': '0x01',
        'authorName': 'koala',
        'authorEmail': 'koala@persper.org',
        'message': 'first commit'
    }
    ccgraph.add_commit(first_commit['hexsha'],
                       first_commit['authorName'],
                       first_commit['authorEmail'],
                       first_commit['message'])
    ccgraph.add_node('f1')
    ccgraph.update_node_history('f1', 10)
    ccgraph.add_node('f2')
    ccgraph.update_node_history('f2', 10)
    ccgraph.add_edge('f1', 'f2')

    func_drs = ccgraph.function_devranks(0.85)
    commit_drs = ccgraph.commit_devranks(0.85)
    dev_drs = ccgraph.developer_devranks(0.85)
    assert(isclose(func_drs['f1'], 0.35, rel_tol=1e-2))
    assert(isclose(func_drs['f2'], 0.65, rel_tol=1e-2))
    assert(isclose(commit_drs[first_commit['hexsha']], 1))
    assert(isclose(dev_drs[first_commit['authorEmail']], 1))

    second_commit = {
        'hexsha': '0x02',
        'authorName': 'beaver',
        'authorEmail': 'beaver@perpser.org',
        'message': 'second commit'
    }
    ccgraph.add_commit(second_commit['hexsha'],
                       second_commit['authorName'],
                       second_commit['authorEmail'],
                       second_commit['message'])
    ccgraph.add_node('f3')
    ccgraph.update_node_history('f3', 10)
    ccgraph.add_edge('f1', 'f3')

    func_drs2 = ccgraph.function_devranks(0.85)
    commit_drs2 = ccgraph.commit_devranks(0.85)
    dev_drs2 = ccgraph.developer_devranks(0.85)
    assert(isclose(func_drs2['f1'], 0.26, rel_tol=1e-2))
    assert(isclose(func_drs2['f2'], 0.37, rel_tol=1e-2))
    assert(isclose(func_drs2['f3'], 0.37, rel_tol=1e-2))
    assert(isclose(commit_drs2[first_commit['hexsha']], 0.63, rel_tol=1e-2))
    assert(isclose(commit_drs2[second_commit['hexsha']], 0.37, rel_tol=1e-2))
    assert(isclose(dev_drs2[first_commit['authorEmail']], 0.63, rel_tol=1e-2))
    assert(isclose(dev_drs2[second_commit['authorEmail']], 0.37, rel_tol=1e-2))

    third_commit = {
        'hexsha': '0x03',
        'authorName': 'koala',
        'authorEmail': 'koala@persper.org',
        'message': 'third commit'
    }
    ccgraph.add_commit(third_commit['hexsha'],
                       third_commit['authorName'],
                       third_commit['authorEmail'],
                       third_commit['message'])
    ccgraph.add_node('f4')
    ccgraph.update_node_history('f4', 10)
    ccgraph.add_edge('f2', 'f4')

    ccgraph.add_node('f5')
    ccgraph.update_node_history('f5', 10)
    ccgraph.add_edge('f2', 'f5')

    func_drs3 = ccgraph.function_devranks(0.85)
    commit_drs3 = ccgraph.commit_devranks(0.85)
    dev_drs3 = ccgraph.developer_devranks(0.85)
    assert(isclose(func_drs3['f1'], 0.141, rel_tol=1e-2))
    assert(isclose(func_drs3['f2'], 0.201, rel_tol=1e-2))
    assert(isclose(func_drs3['f3'], 0.201, rel_tol=1e-2))
    assert(isclose(func_drs3['f4'], 0.227, rel_tol=1e-2))
    assert(isclose(func_drs3['f5'], 0.227, rel_tol=1e-2))
    assert(isclose(commit_drs3[first_commit['hexsha']], 0.343, rel_tol=1e-2))
    assert(isclose(commit_drs3[second_commit['hexsha']], 0.201, rel_tol=1e-2))
    assert(isclose(commit_drs3[third_commit['hexsha']], 0.454, rel_tol=1e-2))
    assert(isclose(dev_drs3[first_commit['authorEmail']], 0.798, rel_tol=1e-2))
    assert(isclose(dev_drs3[second_commit['authorEmail']], 0.201, rel_tol=1e-2))
