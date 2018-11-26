"""
Basic data structures for call graph.
"""
import logging
from io import IOBase
from pathlib import Path, PurePath
from typing import Dict, Iterable, List, NamedTuple, Tuple, Type, Union

import jsonpickle

from persper.analytics.lsp_graph_server.languageclient.lspcontract import \
    DocumentSymbol, Location, Position, SymbolInformation, SymbolKind, \
    TextDocument, TextDocumentContentChangeEvent


_logger = logging.getLogger(__name__)


class CallGraphNode(NamedTuple):
    name: str
    kind: SymbolKind
    file: PurePath
    pos: Position
    length: int

    def __eq__(self, other):
        if not isinstance(other, CallGraphNode):
            return False
        return self.name == other.name and self.file == other.file and self.pos == other.pos and self.length == other.length

    def __hash__(self):
        return hash((self.name, self.kind, self.file, self.pos, self.length))


class CallGraphScope(NamedTuple):
    name: str
    kind: SymbolKind
    file: PurePath
    startPos: Position
    endPos: Position

    def __eq__(self, other):
        if not isinstance(other, CallGraphScope):
            return False
        return self.name == other.name and self.file == other.file and self.startPos == other.startPos \
            and self.endPos == other.endPos

    def __hash__(self):
        return hash((self.name, self.kind, self.file, self.startPos, self.endPos))


class CallGraphBranch(NamedTuple):
    sourceScope: CallGraphScope
    definitionScope: CallGraphScope
    sourceToken: CallGraphNode
    definitionToken: CallGraphNode

    def __eq__(self, other):
        if not isinstance(other, CallGraphBranch):
            return False
        return self.sourceScope == other.sourceScope and self.definitionScope == other.definitionScope \
            and self.sourceToken == other.sourceToken and self.definitionToken == other.definitionToken


class CallGraph():

    def __init__(self):
        self._items = []

    @property
    def items(self):
        return self._items

    def add(self, branch: CallGraphBranch):
        if not branch.sourceScope:
            raise ValueError("branch.sourceScope should not be None.")
        if not branch.definitionScope:
            raise ValueError("branch.definitionScope should not be None.")
        self._items.append(branch)

    def clear(self):
        self._items.clear()

    def removeBySourceFiles(self, fileNames: Iterable[PurePath]):
        if not isinstance(fileNames, set):
            fileNames = set(fileNames)
        newItems = [i for i in self._items if i.sourceScope.file not in fileNames]
        _logger.info("Removed %d branches by %d files.", len(self._items) - len(newItems), len(fileNames))
        self._items = newItems

    def dump(self, file: IOBase):
        for i in self._items:
            file.write(str(i))
            file.write("\n")

    def dumpTo(self, fileName: str):
        with open(fileName, "wt") as f:
            self.dump(f)

    def serialize(self, file: IOBase):
        for item in self._items:
            file.write(jsonpickle.dumps(item, file))
            file.write("\n")
        _logger.info("Written %d call graph branches.", len(self._items))

    def serializeTo(self, fileName):
        with open(fileName, "wt") as f:
            self.serialize(f)

    def deserialize(self, file: IOBase):
        items = []
        for line in file:
            line: str = line.strip()
            if line:
                item = jsonpickle.loads(line)
                if not isinstance(item, CallGraphBranch):
                    raise ValueError("Parsed object [{0}] is not CallGraphBranch.".format(type(item)))
                items.append(item)
        self._items = items
        _logger.info("Loaded %d call graph branches.", len(items))
        assert isinstance(self._items, list)

    def deserializeFrom(self, fileName):
        with open(fileName, "rt") as f:
            self.deserialize(fileName)
