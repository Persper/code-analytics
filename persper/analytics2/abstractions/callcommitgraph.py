from abc import ABC, abstractmethod, abstractproperty
from datetime import datetime
from typing import IO, Collection, Iterable, NamedTuple

from persper.analytics2.abstractions.repository import ICommitInfo


class NodeId(NamedTuple):
    """
    An immutable tuple of node ID.
    """
    name: str
    language: str


class NodeHistoryItem:
    """
    Represents an entry of node history, indicated by the commit hexsha and modified lines of code.
    """

    def __init__(self, hexsha: str = None, added_lines: int = 0, removed_lines: int = 0):
        self.hexsha = hexsha
        self.added_lines = added_lines
        self.removed_lines = removed_lines

    def __repr__(self):
        return "NodeHistoryItem(hexsha={0}, added_lines={1}, removed_lines={2})". \
            format(self.hexsha, self.added_lines, self.removed_lines)

    def __str__(self):
        return "{0}: +{1}, -{2}".format(self.hexsha, self.added_lines, self.removed_lines)


class Node:
    """
    Represents a node in the call commit graph.
    remarks
        The modifications made to this class are not guaranteed to be persisted
        to the call commit graph. Use `IWriteOnlyCallCommitGraph` to make such changes.
    """

    def __init__(self, node_id: NodeId = None, added_by: str = None,
                 history: Collection[NodeHistoryItem] = None, files: Collection[str] = None):
        self._node_id = node_id
        self._added_by = added_by
        self._history = [] if history == None else history
        self._files = [] if files == None else files

    @property
    def node_id(self) -> NodeId:
        return self._node_id

    @node_id.setter
    def node_id(self, value: NodeId):
        if value and not isinstance(value, NodeId):
            raise TypeError(
                "Expect NodeId but {0} is given.".format(type(value)))
        self._node_id = value

    @property
    def added_by(self) -> str:
        """
        Gets the commit hexsha that first added this node.
        """
        return self._added_by

    @added_by.setter
    def added_by(self, value: str):
        self._added_by = value

    @property
    def history(self) -> Collection[NodeHistoryItem]:
        return self._history

    @history.setter
    def history(self, value: Collection[NodeHistoryItem]):
        if value and not isinstance(value, Collection):
            raise TypeError(
                "Expect Collection[NodeHistoryItem] but {0} is given.".format(type(value)))
        self._history = value or []

    @property
    def files(self) -> Iterable[str]:
        return self._files

    @files.setter
    def files(self, value: Collection[str]):
        if value and not isinstance(value, Collection):
            raise TypeError(
                "Expect Collection[str] but {0} is given.".format(type(value)))
        self._files = value or []

    def __repr__(self):
        return "Node(node_id={0}, history=[{1}], files=[{2}])".format(self._node_id, len(self._history), len(self._files))

    def __str__(self):
        return str(self._node_id) or "<anonymous node>"


class Edge:
    """
    Represents an edge in the call commit graph.
    remarks
        The modifications made to this class are not guaranteed to be persisted
        to the call commit graph. Use `IWriteOnlyCallCommitGraph` to make such changes.
    """

    def __init__(self, from_id: NodeId = None, to_id: NodeId = None, added_by: str = None):
        self.from_id = from_id
        # Gets the commit hexsha that first added this edge.
        self.to_id = to_id
        self.added_by = added_by

    def __repr__(self):
        return "Edge(from_id={0}, to_id={1}, added_by={2})".format(self.from_id, self.to_id, self.added_by)

    def __str__(self):
        return "{0} --> {1}".format(self.from_id, self.to_id)


class Commit:
    """
    Represents a commit in the call commit graph storage.
    remarks
        The modifications made to this class are not guaranteed to be persisted
        to the call commit graph. Use `IWriteOnlyCallCommitGraph` to make such changes.
    """

    def __init__(self, hexsha: str, author_email: str, author_name: str, authored_time: datetime,
                 committer_email: str, committer_name: str, committed_time: datetime,
                 message: str, parents: Iterable[str] = None):
        # TODO We need to encapsulate the properties
        self.hexsha = hexsha
        self.author_email = author_email
        self.author_name = author_name
        self.authored_time = authored_time
        self.committer_email = committer_email
        self.committer_name = committer_name
        self.committed_time = committed_time
        self.message = message
        self.parents = parents or ()

    @staticmethod
    def from_commit_info(commit_info: ICommitInfo):
        """
        Creates a new `Commit` instance from the information contained in `ICommitInfo`.
        """
        return Commit(commit_info.hexsha, commit_info.author_email, commit_info.author_name, commit_info.authored_time,
                      commit_info.committer_email, commit_info.committer_name, commit_info.committed_time,
                      commit_info.message, [p.hexsha for p in commit_info.parents])


class IReadOnlyCallCommitGraph(ABC):
    """
    Represents a read-only call commit graph.
    """
    @abstractmethod
    def get_node(self, node_id: NodeId) -> Node:
        """
        Try to get a node from its specified node ID.
        """
        pass

    @abstractmethod
    def enum_nodes(self, name: str = None, language: str = None,
                   from_id: NodeId = None, to_id: NodeId = None) -> Iterable[Node]:
        """
        Enumerates all the nodes that satisfy the given filter condition(s).
        params
            name: filter by node name.
            language: filter by node language.
            from_id: filter by the corresponding call site node.
            to_id: filter by the corresponding defintion node.
        """
        pass

    @abstractmethod
    def get_nodes_count(self, name: str = None, language: str = None,
                        from_id: NodeId = None, to_id: NodeId = None) -> int:
        """
        Gets the count of the nodes that satisfy the given filter condition(s).
        params
            See `enum_nodes` for more information.
        """
        pass

    @abstractmethod
    def get_edge(self, from_id: NodeId, to_id: NodeId) -> Edge:
        """
        Gets the edge connecting the specified nodes indicated by node ID.
        """
        pass

    @abstractmethod
    def enum_edges(self, from_name: str = None, from_language: str = None,
                   to_name: str = None, to_language: str = None) -> Iterable[Edge]:
        """
        Enumerates all the edges that satisfy the given filter condition(s).
        params
            from_name: filter by call site node name.
            from_language: filter by call site node language.
            to_name: filter by defintion node name.
            to_language: filter by defintion node language.
        """
        pass

    @abstractmethod
    def get_edges_count(self, from_name: str = None, from_language: str = None,
                        to_name: str = None, to_language: str = None) -> int:
        """
        Gets the count of all the edges that satisfy the given filter condition(s).
        params
            See `enum_edges` for more information.
        """
        pass

    @abstractmethod
    def get_commit(self, hexsha: str) -> Commit:
        """
        Tries to get the commit information with the specified hexsha.
        """
        pass

    @abstractmethod
    def enum_commits(self) -> Iterable[Commit]:
        """
        Enumerates all the known commits in this call commit graph.
        """
        pass


class IWriteOnlyCallCommitGraph(ABC):
    """
    Represents a write-only call commit graph.
    """
    @abstractmethod
    def update_node_history(self, node_id: NodeId, commit_hexsha: str, added_lines: int = 0, removed_lines: int = 0) -> None:
        """
        Sets or replaces the modification information of the specified node ID and commit hexsha.
        remarks
            If the node does not exist, it will be created.
            If commit_hexsha doesn't exist in history, add the entry to history.
            If commit_hexsha exists in history, the entry will be *replaced*.
                Note the entire node history entry of this hexsha will be replaced rather than merged.
            To accumulate multiple modifications to a node in the same commit, use `NodeHistoryAccumulator` helper class.
        """
        pass

    @abstractmethod
    def update_node_files(self, node_id: NodeId, files: Iterable[str] = None) -> None:
        """
        Sets or replaces the list of files that contains this node in the latest commit.
        Note that this method will replace the whole file list of the specified node.
        """
        pass

    @abstractmethod
    def add_edge(self, from_id: NodeId, to_id: NodeId, commit_hexsha: str) -> None:
        """
        Adds an edge connecting 2 nodes on the specified commit hexsha in the call commit graph.
        It will do nothing if the specified edge already exists.
        params
            from_id: ID of the call site node.
            to_id: ID of the defintion node.
        remarks
            The nodes will be created it either of them does not exist.
        """
        pass

    @abstractmethod
    def update_commit(self, commit: Commit) -> None:
        """
        Adds or updates a commit in the call commit graph.
        It will replace the existing commit if the specified commit hexsha already exists.
        """
        pass

    @abstractmethod
    def flush(self) -> None:
        """
        Ensures all the pending underlying write operations have been performed.
        """
        pass


class ICallCommitGraph(IReadOnlyCallCommitGraph, IWriteOnlyCallCommitGraph):
    """
    Represents a readable/writable call commit graph.
    This is the recommended interface to implement for a common call commit graph.
    """
    pass


class IGraphServer(ABC):
    """
    Provides basic functionality to trigger the commit analysis on graph server. 
    """
    @abstractmethod
    def update_graph(self, commit: ICommitInfo) -> None:
        """
        When implemented, updates the call commit graph with the information
        provided by the current commit.
        """
        pass
