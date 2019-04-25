from abc import ABC, abstractmethod, abstractproperty
from typing import IO, Iterable, NamedTuple

from persper.analytics2.abstractions.repository import ICommitInfo


class NodeId(NamedTuple):
    """
    An immutable tuple of node ID.
    """
    name: str
    language: str


class NodeHistoryItem:
    def __init__(self, commit_id: str = None, added_lines: int = 0, removed_lines: int = 0):
        self.commit_id = commit_id
        self.added_lines = added_lines
        self.removed_lines = removed_lines

    def __repr__(self):
        return "NodeHistoryItem(commit_id={0}, added_lines={1}, removed_lines={2})". \
            format(self.commit_id, self.added_lines, self.removed_lines)

    def __str__(self):
        return "{0}: +{1}, -{2}".format(self.commit_id, self.added_lines, self.removed_lines)


class Node:
    def __init__(self, id: NodeId = None, added_by: str = None,
                 history: Iterable[NodeHistoryItem] = None, files: Iterable[str] = None):
        self._id = id
        self._added_by = added_by
        self._history = history or ()
        self._files = files or ()

    @property
    def id(self) -> NodeId:
        return self._id

    @id.setter
    def id(self, value: NodeId):
        if value and not isinstance(value, NodeId):
            raise TypeError(
                "Expect NodeId but {0} is given.".format(type(value)))
        self._id = value

    @property
    def added_by(self) -> str:
        return self._added_by

    @added_by.setter
    def added_by(self, value: str):
        self._added_by = value

    @property
    def history(self) -> Iterable[NodeHistoryItem]:
        return self._history

    @history.setter
    def history(self, value: Iterable[NodeHistoryItem]):
        if value and not isinstance(value, Iterable):
            raise TypeError(
                "Expect Iterable[NodeHistoryItem] but {0} is given.".format(type(value)))
        self._history = value or ()

    @property
    def files(self) -> Iterable[str]:
        return self._history

    @files.setter
    def files(self, value: Iterable[str]):
        if value and not isinstance(value, Iterable):
            raise TypeError(
                "Expect Iterable[str] but {0} is given.".format(type(value)))
        self._files = value or ()

    def __repr__(self):
        return "Node(id={0}, history=[{1}], files=[{2}])".format(self._id, len(self._history), len(self._files))

    def __str__(self):
        return str(self._id) or "<anonymous node>"


class Edge:
    def __init__(self, from_id: NodeId = None, to_id: NodeId = None, added_by: str = None):
        self.from_id = from_id
        self.to_id = to_id
        # added_by is a commit ID
        self.added_by = added_by

    def __repr__(self):
        return "Edge(from_id={0}, to_id={1}, added_by={2})".format(self.from_id, self.to_id, self.added_by)

    def __str__(self):
        return "{0} --> {1}".format(self.from_id, self.to_id)


class Commit:
    def __init__(self, hex_sha: str, author_email: str, author_name: str, author_date: str,
                 committer_email: str, committer_name: str, commit_date: str, message: str,
                 parent: Iterable[str] = None):
        self.hex_sha = hex_sha
        self.author_email = author_email
        self.author_name = author_name
        self.author_date = author_date
        self.committer_email = committer_email
        self.committer_name = committer_name
        self.commit_date = commit_date
        self.message = message
        self.parent = parent

    @property
    def parent(self) -> Iterable[str]:
        return self.parent

    @parent.setter
    def parent(self, value: Iterable[str]):
        self._parent = value


class IReadOnlyCallCommitGraph(ABC):
    @abstractmethod
    def get_node(self, id: NodeId) -> Node:
        pass

    @abstractmethod
    def enum_nodes(self, name: str = None, language: str = None, from_id: NodeId = None, to_id: NodeId = None) -> \
            Iterable[Node]:
        pass

    @abstractmethod
    def get_nodes_count(self, name: str = None, language: str = None, from_id: NodeId = None,
                        to_id: NodeId = None) -> int:
        pass

    @abstractmethod
    def get_edge(self, from_id: NodeId, to_id: NodeId) -> Edge:
        pass

    @abstractmethod
    def enum_edges(self, from_name: str = None, from_language: str = None, to_name: str = None,
                   to_language: str = None) -> Iterable[Edge]:
        pass

    @abstractmethod
    def get_edges_count(self, from_name: str = None, from_language: str = None, to_name: str = None,
                        to_language: str = None) -> int:
        pass

    @abstractmethod
    def get_commit(self, hex_sha: str) -> Commit:
        pass

    @abstractmethod
    def get_commits(self) -> Iterable[Commit]:
        pass


class IWriteOnlyCallCommitGraph(ABC):
    @abstractmethod
    def add_node(self, id: NodeId, commit_hex_sha: str) -> None:
        """Add Node
        :param id:
        :param commit_hex_sha: if added_by is not set
        :return:
        """
        pass

    @abstractmethod
    def add_node_history(self, id: NodeId, commit_hex_sha: str, added_lines: int, removed_lines: int) -> None:
        """Add Node History
        if commit_hex_sha doesn't exist in history, add the entry to history.
        if commit_hex_sha exists in history, sum existing added_lines/removed_lines and new one
        """
        pass

    @abstractmethod
    def add_node_file(self, id: NodeId, file: str) -> None:
        pass

    @abstractmethod
    def add_edge(self, from_id: NodeId, to_id: NodeId, commit_hex_sha: str) -> None:
        pass

    @abstractmethod
    def add_commit(self, hex_sha: str, author_email: str, author_name: str, author_date: str,
                   committer_email: str, committer_name: str, commit_date: str, message: str) -> None:
        pass

    def add_commit_parent(self, hex_sha: str, parent: str) -> None:
        pass

    @abstractmethod
    def flush(self) -> None:
        pass


class ICallCommitGraph(IReadOnlyCallCommitGraph, IWriteOnlyCallCommitGraph):
    pass


class IGraphServer(ABC):
    @abstractmethod
    def update_graph(self, commit: ICommitInfo) -> None:
        pass
