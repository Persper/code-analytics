import logging
import sys
from collections import defaultdict

from persper.analytics2.abstractions.callcommitgraph import (Commit, Edge,
                                                             ICallCommitGraph,
                                                             Node,
                                                             NodeHistoryItem,
                                                             NodeId)
from persper.analytics2.abstractions.repository import (
    ICommitInfo, IRepositoryHistoryProvider)
from typing import Iterable

class MemoryCallCommitGraph(ICallCommitGraph):
    def __init__(self, graph_data: dict = None):
        self._nodes_dict = {}
        self._edges_dict = {}
        self._commits = {}
        self._from_edges = defaultdict(list)
        self._to_edges = defaultdict(list)
        if graph_data:
            for i in graph_data["nodes"]:
                nodeid = NodeId(i["id"]['name'], i["id"]['language'])
                for commit_id, history in i['history'].items:
                    self.update_node_history(
                        nodeid, commit_id, history['adds'], history['dels'])
                files = []
                for file in i["files"]:
                    files.append(file)
                self.update_node_files(nodeid, files)
            for i in graph_data["edges"]:
                from_id = NodeId(i['from_id']["name"],
                                 i['from_id']["language"])
                to_id = NodeId(i['to_id']["name"], i['to_id']["language"])
                self.add_edge(from_id, to_id, i["added_by"])

            for i in graph_data["commits"]:
                self.add_commit(i["hex_sha"], Commit(i["hex_sha"], i["author_email"], i['author_name'],
                                                     i['author_date'], i['committer_email'],
                                                     i['committer_name'], i['commit_date'],
                                                     i['message'], i['parent']))

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

    def add_node(self, id: NodeId, node: Node) -> None:
        self._nodes_dict[id] = node

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
        edge = Edge(from_id, to_id, commit_hexsha)
        self._edges_dict[(from_id, to_id)] = edge
        self._from_edges[from_id].append(to_id)
        self._to_edges[to_id].append(from_id)

    def flush(self) -> None:
        pass

    def add_commit(self, hex_sha: str, author_email: str, author_name: str, author_date: str,
                   committer_email: str, committer_name: str, commit_date: str, message: str) -> None:
        self._commits[hex_sha] = Commit(hex_sha, author_email, author_name,
                                        author_date, committer_email, committer_name, commit_date, message)

    def get_commit(self, hex_sha: str) -> Commit:
        return self._commits[hex_sha]

    def update_commit(self, commit: Commit) -> None:
        self._commits[commit.hexsha] = commit
