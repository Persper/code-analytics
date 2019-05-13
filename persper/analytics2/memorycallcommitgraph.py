import json
import logging
import sys
from collections import defaultdict
from typing import Iterable, TextIO

from persper.analytics2.abstractions.callcommitgraph import (Commit, Edge,
                                                             ICallCommitGraph,
                                                             Node,
                                                             NodeHistoryItem,
                                                             NodeId)
from persper.analytics2.abstractions.repository import (ICommitInfo,
                                                        ICommitRepository)


def serialize_node_id(d: NodeId) -> dict:
    return {"name": d.name, "language": d.language}


def deserialize_node_id(d: dict) -> NodeId:
    return NodeId(d["name"], d["language"])


def deserialize_node_history_item(d: dict) -> NodeHistoryItem:
    return NodeHistoryItem(hexsha=d["hexsha"], added_lines=d["added_lines"], removed_lines=d["removed_lines"])


def deserialize_node(d: dict) -> NodeId:
    return Node(node_id=deserialize_node_id(d["id"]), added_by=d["added_by"],
                history=[deserialize_node_history_item(i) for i in d["history"]],
                files=list(d["files"]))


def deserialize_edge(d: dict) -> Edge:
    return Edge(from_id=deserialize_node_id(d["from_id"]), to_id=d["to_id"], added_by=d["added_by"])


def deserialize_commit(d: dict) -> Commit:
    return Commit(d["hex_sha"],
                  d["author_email"], d['author_name'], d['author_date'],
                  d['committer_email'], d['committer_name'], d['commit_date'],
                  d['message'], d['parents'])


class MemoryCallCommitGraph(ICallCommitGraph):
    def __init__(self):
        self._nodes_dict = {}
        self._edges_dict = {}
        self._commits = {}
        self._from_edges = defaultdict(list)
        self._to_edges = defaultdict(list)

    @staticmethod
    def deserialize_dict(graph_data: dict) -> "MemoryCallCommitGraph":
        graph = MemoryCallCommitGraph()
        for nd in graph_data["nodes"]:
            node = deserialize_node(nd)
            graph._add_node_direct(node)
        for ed in graph_data["edges"]:
            edge = deserialize_edge(ed)
            graph._add_edge_direct(edge)
        for cd in graph_data["commits"]:
            commit = deserialize_commit(cd)
            graph.update_commit(commit)
        return graph

    @staticmethod
    def load_from(fp: TextIO) -> "MemoryCallCommitGraph":
        d = json.load(fp)
        return MemoryCallCommitGraph.deserialize_dict(d)

    @staticmethod
    def load(json_content: str) -> "MemoryCallCommitGraph":
        d = json.loads(json_content)
        return MemoryCallCommitGraph.deserialize_dict(d)

    def _ensure_node_exists(self, node_id: NodeId, commit_hexsha: str) -> None:
        if node_id not in self._nodes_dict:
            self._nodes_dict[node_id] = Node(node_id, added_by=commit_hexsha)
        assert self._nodes_dict[node_id].added_by

    def get_node(self, id: NodeId) -> Node:
        return self._nodes_dict.get(id, None)

    def get_nodes_count(self, name: str = None, language: str = None,
                        from_id: NodeId = None, to_id: NodeId = None) -> int:
        base_set = self._nodes_dict.values()
        if name is None and language is None and from_id is None and to_id is None:
            return len(base_set)
        count = 0
        for node in base_set:
            if name is not None and node.node_id.name != name:
                continue
            if language is not None and node.node_id.language != language:
                continue
            if from_id is not None and node in self._from_edges[from_id]:
                continue
            if to_id is not None and node in self._to_edges[to_id]:
                continue
            count += 1
        return count

    def get_edge(self, from_id: NodeId, to_id: NodeId) -> Edge:
        return self._edges_dict[(from_id, to_id)]

    def get_edges_count(self, from_name: str = None, from_language: str = None, to_name: str = None,
                        to_language: str = None) -> int:
        base_set = self._edges_dict.values()
        if from_name is None and from_language is None and to_name is None and to_language is None:
            return len(base_set)
        count = 0
        for edge in base_set:
            if from_name is not None and edge.from_id.name != from_name:
                continue
            if to_name is not None and edge.to_id.name != to_name:
                continue
            if from_language is not None and edge.from_id.language != from_language:
                continue
            if to_language is not None and edge.to_id.language != to_language:
                continue
            count += 1
        return count

    def enum_edges(self, from_name: str = None, from_language: str = None, to_name: str = None, to_language: str = None) -> Iterable[Edge]:
        base_set = self._edges_dict.values()
        for edge in base_set:
            if from_name is not None and edge.from_id.name != from_name:
                continue
            if to_name is not None and edge.to_id.name != to_name:
                continue
            if from_language is not None and edge.from_id.language != from_language:
                continue
            if to_language is not None and edge.to_id.language != to_language:
                continue
            yield edge

    def enum_nodes(self, name: str = None, language: str = None, from_id: NodeId = None, to_id: NodeId = None) -> Iterable[Node]:
        base_set = self._nodes_dict.values()
        for node in base_set:
            if name is not None and node.name != name:
                continue
            if language is not None and node.language != language:
                continue
            if from_id is not None and node in self._from_edges[from_id]:
                continue
            if to_id is not None and node in self._to_edges[to_id]:
                continue
        yield node

    def enum_commits(self) -> Iterable[Commit]:
        for commit in self._commits.values():
            yield commit

    def _add_node_direct(self, node: Node) -> None:
        self._nodes_dict[node.id] = node

    def update_node_history(self, node_id: NodeId, commit_hexsha: str,
                            added_lines: int = 0, removed_lines: int = 0) -> None:
        self._ensure_node_exists(node_id, commit_hexsha)
        for historyitem in self._nodes_dict[node_id].history:
            if historyitem.hexsha == commit_hexsha:
                self._nodes_dict[node_id].history = [NodeHistoryItem(commit_hexsha,
                                                                     added_lines, removed_lines)]
            return
        self._nodes_dict[node_id].history.append(NodeHistoryItem(commit_hexsha,
                                                                 added_lines, removed_lines))

    def update_node_files(self, node_id: NodeId, commit_hexsha: str,
                          files: Iterable[str] = None) -> None:
        self._ensure_node_exists(node_id, commit_hexsha)
        self._nodes_dict[node_id].files = files

    def add_edge(self, from_id: NodeId, to_id: NodeId, commit_hexsha: str) -> None:
        self._add_edge_direct(Edge(from_id, to_id, commit_hexsha))

    def _add_edge_direct(self, edge: Edge) -> None:
        self._edges_dict[(edge.from_id, edge.to_id)] = edge
        self._from_edges[edge.from_id].append(edge.to_id)
        self._to_edges[edge.to_id].append(edge.from_id)

    def flush(self) -> None:
        pass

    def get_commit(self, hex_sha: str) -> Commit:
        return self._commits.get(hex_sha, None)

    def update_commit(self, commit: Commit) -> None:
        self._commits[commit.hexsha] = commit
