import os
from datetime import datetime, timedelta
from random import randint
from typing import Iterable

from persper.analytics2.abstractions.callcommitgraph import (Commit, Edge,
                                                             ICallCommitGraph,
                                                             Node, NodeId)

def commit_equals(x: Commit, y: Commit):
    if not x or not y:
        return not x and not y
    return (x.hexsha == y.hexsha and
            x.author_email == y.author_email and
            x.author_name == y.author_name and
            x.authored_time == y.authored_time and
            x.committer_email == y.committer_email and
            x.committer_name == y.committer_name and
            x.committed_time == y.committed_time and
            x.message == y.message and
            list(x.parents) == list(y.parents))


def create_dummy_commit(message: str = None, parents: Iterable[str] = None):
    return Commit("000000000011111111112222222222{:010x}".format(randint(0, 0xffffffffff)),
                  "example@company.org", "example", datetime.now() - timedelta(seconds=10),
                  "example@company.org", "example", datetime.now(),
                  message or "Created by create_dummy_commit.",
                  list(parents) if parents else ())


def test_call_commit_graph(ccg: ICallCommitGraph):
    #assert ccg
    # commits
    commit1 = create_dummy_commit()
    commit2 = create_dummy_commit()
    commit3 = create_dummy_commit("Merge commit.", [commit1.hexsha, commit2.hexsha])
    ccg.update_commit(commit1)
    ccg.update_commit(commit2)
    ccg.update_commit(commit3)
    ccg.flush()

    commit = ccg.get_commit(commit1.hexsha)
    assert commit_equals(commit, commit1)
    commit = ccg.get_commit(commit2.hexsha)
    assert commit_equals(commit, commit2)
    commit = ccg.get_commit(commit3.hexsha)
    assert commit_equals(commit, commit3)

    # nodes
    cppnode1 = NodeId("test_ns::MyClass::func(int, int)", "cpp")
    cppnode2 = NodeId("test_ns::MyClass::foo()", "cpp")
    cppnode3 = NodeId("test_ns::MyClass::bar()", "cpp")
    csnode1 = NodeId("TestNS.Wrappers.MyClass.Func(int, int)", "cs")
    csnode2 = NodeId("TestNS.Wrappers.MyClass.Foo()", "cs")
    csnode3 = NodeId("TestNS.Wrappers.MyClass.Bar()", "cs")
    javanode1 = NodeId("TestNS.Wrappers.MyClass.Foo()", "java")
    cppFiles = ["MyClass.h", "MyClass.cpp"]
    csFiles = ["MyClass.cs"]
    ccg.update_node_files(cppnode1, added_files=cppFiles)
    ccg.update_node_files(cppnode2, added_files=cppFiles)
    ccg.update_node_files(cppnode3, added_files=cppFiles)
    ccg.update_node_files(csnode2, added_files=csFiles)
    ccg.update_node_files(csnode3, added_files=csFiles)
    ccg.update_node_files(javanode1, added_files=["MyClass.java"])
    ccg.update_node_history(cppnode1, commit1.hexsha, 10, 0)
    # 10 will be overwritten
    ccg.update_node_history(cppnode1, commit1.hexsha, 20, -10)
    ccg.update_node_history(cppnode2, commit1.hexsha, 15, 0)
    ccg.update_node_history(cppnode3, commit1.hexsha, 10, 0)
    ccg.update_node_history(csnode2, commit2.hexsha, 5, 0)
    ccg.update_node_history(csnode3, commit2.hexsha, 4, 0)
    ccg.add_edge(cppnode2, cppnode1, commit1.hexsha)
    ccg.add_edge(cppnode3, cppnode1, commit1.hexsha)
    # csnode1 is implicitly added
    ccg.add_edge(csnode1, cppnode1, commit3.hexsha)
    ccg.add_edge(csnode2, csnode1, commit1.hexsha)
    ccg.add_edge(csnode3, csnode2, commit1.hexsha)
    ccg.flush()

    assert ccg.get_nodes_count() == 7
    assert ccg.get_nodes_count(name=csnode2.name) == 2
    assert ccg.get_nodes_count(name=csnode2.name, language=csnode2.language) == 1
    assert ccg.get_nodes_count(name="non_existent") == 0
    assert ccg.get_nodes_count(language="cpp") == 3
    assert ccg.get_nodes_count(language="cs") == 3
    assert ccg.get_nodes_count(language="java") == 1
    assert ccg.get_nodes_count(language="java") == 1
    assert ccg.get_nodes_count(language="non_existent") == 0
    assert ccg.get_edges_count() == 5
    assert ccg.get_edges_count(from_language="cs") == 3
    assert ccg.get_edges_count(to_language="cpp") == 4
    assert ccg.get_edges_count(from_language="cs", to_language="cpp") == 1
    assert ccg.get_edges_count(to_name=cppnode1.name) == 3

    def assertNode(node_id, added_by, files):
        node = ccg.get_node(node_id)
        assert node
        assert node.node_id == node_id
        assert node.added_by == added_by
        assert set(node.files) == set(files)
        return node

    assert ccg.get_node(NodeId("non_existent", "cpp")) == None
    assert ccg.get_node(NodeId(cppnode1.name, "non_existent")) == None
    assertNode(cppnode1, added_by=commit1.hexsha, files=cppFiles)
    assertNode(cppnode2, added_by=commit1.hexsha, files=cppFiles)
    assertNode(cppnode3, added_by=commit1.hexsha, files=cppFiles)
    assertNode(csnode1, added_by=commit3.hexsha, files=csFiles)
    assertNode(csnode2, added_by=commit2.hexsha, files=csFiles)
    assertNode(csnode3, added_by=commit2.hexsha, files=csFiles)
