from abc import ABC, abstractclassmethod, abstractproperty
from typing import IO, Iterable, NamedTuple

from .repository import ICommitInfo


class NodeId(NamedTuple):
    """
    An immutable tuple of node ID.
    """
    name: str
    language: str


class Node():
    def __init__(self):
        pass

    # TODO add other members


class Edge():
    def __init__(self):
        pass

    # TODO add other members


class IReadOnlyCallCommitGraph(ABC):
    @abstractclassmethod
    def get_node(id: NodeId) -> Node:
        return Node()

    @abstractclassmethod
    def get_edge(from_id: NodeId, to_id: NodeId) -> Edge:
        return Edge()

    @abstractclassmethod
    def get_nodes_count(language: str = None, from_id: NodeId = None, to_id: NodeId = None) -> Iterable[Edge]:
        return None

    @abstractclassmethod
    def enum_nodes(language: str = None, from_id: NodeId = None, to_id: NodeId = None) -> Iterable[Edge]:
        return None

    @abstractclassmethod
    def get_edges_count(from_name: str = None, from_language: str = None, to_name: str = None, to_language: str = None) -> Iterable[Edge]:
        return None

    @abstractclassmethod
    def enum_edges(from_name: str = None, from_language: str = None, to_name: str = None, to_language: str = None) -> Iterable[Edge]:
        return None


class IWriteOnlyCallCommitGraph(ABC):
    @abstractclassmethod
    def add_node(id: NodeId) -> bool:
        return False

    @abstractclassmethod
    def add_node_history(id: NodeId, commit_id: str, added_lines: int, removed_lines: int) -> bool:
        return False

    @abstractclassmethod
    def add_edge(commit_id: str, from_id: NodeId, to_id: NodeId) -> bool:
        return False


class ICallCommitGraph(IReadOnlyCallCommitGraph, IWriteOnlyCallCommitGraph):
    pass


class IGraphServer(ABC):
    @abstractclassmethod
    def update_graph(self, commit: ICommitInfo) -> None:
        pass
