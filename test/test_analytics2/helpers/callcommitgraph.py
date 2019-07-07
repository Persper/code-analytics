import os
from datetime import datetime, timedelta
from random import randint
from typing import Iterable

from persper.analytics2.abstractions.callcommitgraph import (
    Commit, Edge, ICallCommitGraph, IReadOnlyCallCommitGraph, Node,
    NodeHistoryItem, NodeId)


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
    # assert ccg
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
    javaFiles = ["MyClass.java"]
    ccg.update_node_files(cppnode1, commit1.hexsha, files=cppFiles)
    ccg.update_node_files(cppnode2, commit1.hexsha, files=cppFiles)
    ccg.update_node_files(cppnode3, commit1.hexsha, files=cppFiles)
    ccg.update_node_files(csnode2, commit2.hexsha, files=csFiles)
    ccg.update_node_files(csnode3, commit2.hexsha, files=csFiles)
    ccg.update_node_files(javanode1, commit3.hexsha, files=javaFiles)
    ccg.update_node_history(cppnode1, commit1.hexsha, 10, 0)
    # (10, 0) will be overwritten
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

    EXPECTED_NODE_IDS = {cppnode1, cppnode2, cppnode3, csnode1, csnode2, csnode3, javanode1}
    assert ccg.get_nodes_count() == len(EXPECTED_NODE_IDS)
    assert set((n.node_id for n in ccg.enum_nodes())) == EXPECTED_NODE_IDS
    assert ccg.get_nodes_count(name=csnode2.name) == 2
    assert ccg.get_nodes_count(name=csnode2.name, language=csnode2.language) == 1
    assert ccg.get_nodes_count(name="non_existent") == 0
    assert ccg.get_nodes_count(language="cpp") == 3
    assert ccg.get_nodes_count(language="cs") == 3
    assert ccg.get_nodes_count(language="java") == 1
    assert ccg.get_nodes_count(language="java") == 1
    assert ccg.get_nodes_count(language="non_existent") == 0

    EXPECTED_EDGES = {
        (cppnode2, cppnode1),
        (cppnode3, cppnode1),
        (csnode1, cppnode1),
        (csnode2, csnode1),
        (csnode3, csnode2)
    }

    def assert_edges_same(actual_edges, expected_ids):
        actual_edges = set(((e.from_id, e.to_id) for e in actual_edges))
        if not isinstance(expected_ids, set):
            expected_ids = set(expected_ids)
        assert actual_edges == expected_ids

    assert ccg.get_edges_count() == len(EXPECTED_EDGES)
    assert_edges_same(ccg.enum_edges(), EXPECTED_EDGES)
    assert ccg.get_edges_count(from_language="cs") == 3
    assert_edges_same(ccg.enum_edges(from_language="cs"), (e for e in EXPECTED_EDGES if e[0].language == "cs"))
    assert ccg.get_edges_count(to_language="cpp") == 3
    assert_edges_same(ccg.enum_edges(to_language="cpp"), (e for e in EXPECTED_EDGES if e[1].language == "cpp"))
    assert ccg.get_edges_count(from_language="cs", to_language="cpp") == 1
    assert_edges_same(ccg.enum_edges(from_language="cs", to_language="cpp"),
                      (e for e in EXPECTED_EDGES if e[0].language == "cs" and e[1].language == "cpp"))
    assert ccg.get_edges_count(to_name=cppnode1.name) == 3
    assert_edges_same(ccg.enum_edges(to_name=cppnode1.name),
                      (e for e in EXPECTED_EDGES if e[1].name == cppnode1.name))

    def assertNode(node_id, added_by, files):
        node = ccg.get_node(node_id)
        assert node
        assert node.node_id == node_id
        assert node.added_by == added_by
        assert set(node.files) == set(files)

        return node

    assert ccg.get_node(NodeId("non_existent", "cpp")) is None
    assert ccg.get_node(NodeId(cppnode1.name, "non_existent")) is None
    assertNode(cppnode1, added_by=commit1.hexsha, files=cppFiles)
    assertNode(cppnode2, added_by=commit1.hexsha, files=cppFiles)
    assertNode(cppnode3, added_by=commit1.hexsha, files=cppFiles)
    assertNode(csnode1, added_by=commit3.hexsha, files=[])
    assertNode(csnode2, added_by=commit2.hexsha, files=csFiles)
    assertNode(csnode3, added_by=commit2.hexsha, files=csFiles)
    assertNode(javanode1, added_by=commit3.hexsha, files=javaFiles)


def commit_assertion_skip(expectedGraph, actualGraph, expectedHexsha, actualHexsha):
    pass


def commit_assertion_by_hexsha(expectedGraph, actualGraph, expectedHexsha, actualHexsha):
    assert expectedHexsha == actualHexsha, "Commits are not the same by hexsha."


def commit_assertion_by_comment(expectedGraph, actualGraph, expectedHexsha, actualHexsha):
    c1 = expectedGraph.get_commit(expectedHexsha)
    c2 = actualGraph.get_commit(actualHexsha)
    assert c1, "Expected-side of commit is missing."
    assert c2, "Actual-side of commit is missing."
    c1_message = (c1.message or "").strip()
    c2_message = (c2.message or "").strip()
    assert c1_message == c2_message, \
        "Commits are not the same by commit message. Expected: {0!r}; actual: {1!r}".format(c1_message, c2_message)


def assert_graph_same(expected: IReadOnlyCallCommitGraph, actual: IReadOnlyCallCommitGraph,
                      commit_assertion=commit_assertion_by_hexsha):
    """
    Asserts two `IReadOnlyCallCommitGraph` instances contain the equivalent content.
    params
        commit_assertion:   Specifies how to treat two commits as equivalent. You need to choose between
                            `commit_assertion_skip`, `commit_assertion_by_hexsha`, and `commit_assertion_by_comment`.
    """
    def assertCommitEqual(expectedHexsha, actualHexsha):
        return commit_assertion(expected, actual, expectedHexsha, actualHexsha)
    for n1 in expected.enum_nodes():
        n2 = actual.get_node(n1.node_id)
        assert n2, "Node missing: {0}".format(n1.node_id)
        assert n1.node_id == n2.node_id
        assertCommitEqual(n1.added_by, n2.added_by)
        keyExtractor = None
        if commit_assertion == commit_assertion_by_hexsha:
            # Make autopep8 happy.
            def f(h):
                return h.hexsha
            keyExtractor = f
        elif commit_assertion == commit_assertion_by_comment:
            def f(h):
                return h.message
            keyExtractor = f
        if keyExtractor:
            d1 = dict((keyExtractor, h) for h in n1.history)
            d2 = dict((keyExtractor, h) for h in n2.history)
            for k, h1 in d1.items():
                h2 = d2.get(k, None)
                assert isinstance(h1, NodeHistoryItem)
                assert h2, "Commit history {0} missing for node {1}.".format(h1, n1.node_id)
                assert isinstance(h2, NodeHistoryItem)
                assert h1.added_lines == h2.added_lines, "In commit: {0}".format(h1)
                assert h1.removed_lines == h2.removed_lines, "In commit: {0}".format(h1)
            if len(d1) < len(d2):
                # there are extra node history
                for k, h2 in d2:
                    h1 = d1.get(k, None)
                    assert h2, "Extra commit history {0} for node {1}.".format(h1, n1.node_id)
        assert set(n1.files) == set(n2.files)
    if expected.get_nodes_count() < actual.get_nodes_count():
        # there are extra nodes
        for n2 in actual.enum_nodes():
            n1 = expected.get_node(n2.node_id)
            assert n1, "Extra node: {0}".format(n2.node_id)
    for b1 in expected.enum_edges():
        b2 = actual.get_edge(b1.from_id, b1.to_id)
        assert b2, "Edge missing: {0} -> {1}".format(b1.from_id, b1.to_id)
        assertCommitEqual(b1.added_by, b2.added_by)
    if expected.get_edges_count() < actual.get_edges_count():
        # there are extra edges
        for n2 in actual.enum_edges():
            n1 = expected.get_edge(n2.from_id, n2.to_id)
            assert n1, "Extra edge: {0} -> {1}".format(b2.from_id, b2.to_id)
