from abc import ABC, abstractclassmethod, abstractproperty
from typing import IO, Iterable, NamedTuple

from .repository import ICommitInfo


class NodeId(NamedTuple):
    """
    An immutable tuple of node ID.
    """
    name: str
    language: str


class NodeHistoryItem():
    def __init__(self, commit_id: str = None, added_lines: int = 0, removed_lines: int = 0):
        self.commit_id = commit_id
        self.added_lines = added_lines
        self.removed_lines = removed_lines

    def __repr__(self):
        return "NodeHistoryItem(commit_id={0}, added_lines={1}, removed_lines={2})".format(self.commit_id, self.added_lines, self.removed_lines)

    def __str__(self):
        return "{0}: +{1}, -{2}".format(self.commit_id, self.added_lines, self.removed_lines)


class Node():
    def __init__(self, id: NodeId = None, history: Iterable[NodeHistoryItem] = None, files: Iterable[str] = None):
        self._id = id
        self._history = history or ()
        self._files = files or ()

    @property
    def id(self):
        return self._id

    @id.setter
    def id(self, value):
        if value and not isinstance(value, NodeId):
            raise TypeError(
                "Expect NodeId but {0} is given.".format(type(value)))
        self._id = value

    @property
    def history(self):
        return self._history

    @history.setter
    def history(self, value):
        if value and not isinstance(value, Iterable):
            raise TypeError(
                "Expect Iterable[NodeHistoryItem] but {0} is given.".format(type(value)))
        self._history = value or ()

    @property
    def files(self):
        return self._history

    @files.setter
    def files(self, value):
        if value and not isinstance(value, Iterable):
            raise TypeError(
                "Expect Iterable[str] but {0} is given.".format(type(value)))
        self._files = value or ()

    def __repr__(self):
        return "Node(id={0}, history=[{1}], files=[{2}])".format(self._id, len(self._history), len(self._files))

    def __str__(self):
        return str(self._id) or "<anonymous node>"


class Edge():
    def __init__(self, from_id: NodeId = None, to_id: NodeId = None, added_by: str = None):
        self.from_id = from_id
        self.to_id = to_id
        # added_by is a commit ID
        self.added_by = added_by

    def __repr__(self):
        return "Edge(from_id={0}, to_id={1}, added_by={2})".format(self.from_id, self.to_id, self.added_by)

    def __str__(self):
        return "{0} --> {1}".format(self.from_id, self.to_id)


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
    def add_node(id: NodeId) -> None:
        pass

    @abstractclassmethod
    def add_node_history(id: NodeId, commit_id: str, added_lines: int, removed_lines: int) -> None:
        pass

    @abstractclassmethod
    def add_edge(commit_id: str, from_id: NodeId, to_id: NodeId) -> None:
        pass


class ICallCommitGraph(IReadOnlyCallCommitGraph, IWriteOnlyCallCommitGraph):
    pass


class IGraphServer(ABC):
    @abstractclassmethod
    def update_graph(self, commit: ICommitInfo) -> None:
        pass
