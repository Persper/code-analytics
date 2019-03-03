import pathlib
from enum import Enum
from typing import Tuple, Union
import logging
import os

_logger = logging.getLogger(__name__)


class MessageType(Enum):
    Error = 1
    Warning = 2
    Info = 3
    Log = 4


class SymbolKind(Enum):
    Unknown = 0
    File = 1
    Module = 2
    Namespace = 3
    Package = 4
    Class = 5
    Method = 6
    Property = 7
    Field = 8
    Constructor = 9
    Enum = 10
    Interface = 11
    Function = 12
    Variable = 13
    Constant = 14
    String = 15
    Number = 16
    Boolean = 17
    Array = 18
    Object = 19
    Key = 20
    Null = 21
    EnumMember = 22
    Struct = 23
    Event = 24
    Operator = 25
    TypeParameter = 26

    # cquery extensions
    # See also https://github.com/Microsoft/language-server-protocol/issues/344
    # for new SymbolKind clang/Index/IndexSymbol.h clang::index::SymbolKind
    TypeAlias = 252
    Parameter = 253
    StaticMethod = 254
    Macro = 255


class CompletionItemKind(Enum):
    Text = 1
    Method = 2
    Function = 3
    Constructor = 4
    Field = 5
    Variable = 6
    Class = 7
    Interface = 8
    Module = 9
    Property = 10
    Unit = 11
    Value = 12
    Enum = 13
    Keyword = 14
    Snippet = 15
    Color = 16
    File = 17
    Reference = 18
    Folder = 19
    EnumMember = 20
    Constant = 21
    Struct = 22
    Event = 23
    Operator = 24
    TypeParameter = 25


class LspContractObject:
    def __init__(self):
        pass

    def __repr__(self):
        return self.__str__()


class Position(LspContractObject):
    """
    Line position in a document (zero-based).
    """

    def __init__(self, line: int, character: int):
        self.line = line
        self.character = character

    def __str__(self):
        return str(self.line) + "," + str(self.character)

    def __eq__(self, other: "Position"):
        return self.line == other.line and self.character == other.character

    def __ne__(self, other: "Position"):
        return self.line != other.line or self.character != other.character

    def __le__(self, other: "Position"):
        return self.line < other.line or self.line == other.line and self.character <= other.character

    def __lt__(self, other: "Position"):
        return self.line < other.line or self.line == other.line and self.character < other.character

    def toTuple(self):
        return (self.line, self.character)

    def toDict(self):
        return {"line": self.line, "character": self.character}

    @staticmethod
    def fromDict(d: dict):
        return Position(d["line"], d["character"])

    @staticmethod
    def parse(expr: Union[Tuple[int, int], "Position"]):
        if isinstance(expr, Position):
            return expr
        if isinstance(expr, (list, tuple)):
            return Position(expr[0], expr[1])
        raise TypeError("Invalid expr type.")


class Range(LspContractObject):
    """
    A range in a text document expressed as (zero-based) start and end positions.
    """

    def __init__(self, start: Position, end: Position):
        self.start = start
        self.end = end

    def __str__(self):
        return str(self.start) + "-" + str(self.end)

    def toDict(self):
        return {"start": self.start.toDict(),
                "end": self.end.toDict()}

    @staticmethod
    def fromDict(d: dict):
        return Range(Position.fromDict(d["start"]), Position.fromDict(d["end"]))


class Location(LspContractObject):
    """
    Represents a location inside a resource, such as a line inside a text file.
    """

    def __init__(self, uri: str, range: Range):
        self.uri = uri
        self.range = range

    def __str__(self):
        return str(self.uri) + ":" + str(self.range)

    def toDict(self):
        return {"uri": self.uri, "range": self.range.toDict()}

    @staticmethod
    def fromDict(d: dict):
        return Location(d["uri"], Range.fromDict(d["range"]))


class TextDocument(LspContractObject):
    """
    An item to transfer a text document from the client to the server.
    """

    def __init__(self, uri: str, languageId: str, version: int, text: str):
        self.uri = uri
        self.languageId = languageId
        self.version = version
        self.text = text

    def __str__(self):
        return str.format("{0};{1};[{2}]", self.uri, self.languageId, self.version)

    def toDict(self):
        return {"uri": self.uri, "languageId": self.languageId, "version": self.version, "text": self.text}

    @staticmethod
    def fromDict(d: dict):
        return TextDocument(d["uri"], d["languageId"], d["version"], d["text"])

    @staticmethod
    def loadFile(fileName: str, languageId: str, version: int = 1):
        content = None
        try:
            with open(fileName, "rt", encoding="utf-8", errors="replace") as file:
                content = file.read()
            return TextDocument(TextDocument.fileNameToUri(fileName), languageId, version, content)
        except Exception as ex:
            raise ValueError("Cannot load from {0}.".format(fileName)) from ex

    @staticmethod
    def fileNameToUri(fileName: str):
        return pathlib.Path(fileName).as_uri()


class DocumentSymbol(LspContractObject):
    """
    Represents programming constructs like variables, classes, interfaces etc. that appear in a document. Document symbols can be
    hierarchical and they have two ranges: one that encloses its definition and one that points to its most interesting range,
    e.g. the range of an identifier.
    """

    def __init__(self, name: str, detail: str, kind: SymbolKind, deprecated: bool, range: Range, selectionRange: Range, children: list):
        self.name = name
        self.detail = detail
        self.kind = kind
        self.deprecated = deprecated
        self.range = range
        """
        The range enclosing this symbol not including leading/trailing whitespace but everything else
        like comments. This information is typically used to determine if the clients cursor is
        inside the symbol to reveal in the symbol in the UI.
        """
        self.selectionRange = selectionRange
        """
        The range that should be selected and revealed when this symbol is being picked, e.g the name of a function.
        Must be contained by the `range`.
        """
        self.children = list(children)

    def getSymbolRange(self):
        return self.selectionRange

    def __str__(self):
        return self.name + "[" + self.kind + "]"

    def toDict(self):
        raise NotImplementedError()

    @staticmethod
    def fromDict(d: dict):
        children = ()
        if d.get("children"):
            children = (DocumentSymbol.fromDict(cd) for cd in d["children"])
        return DocumentSymbol(d["name"], d.get("detail"), SymbolKind(d["kind"] if d["kind"] else 0),
                              d.get("deprecated"), Range.fromDict(d["range"]), Range.fromDict(d["selectionRange"]),
                              children)


class SymbolInformation(LspContractObject):
    """
    Represents information about programming constructs like variables, classes,
    interfaces etc.
    """

    def __init__(self, name: str, kind: SymbolKind, deprecated: bool, location: Location, containerName: str):
        self.name = name
        self.kind = kind
        self.deprecated = deprecated
        self.location = location
        self.containerName = containerName

    def getSymbolRange(self):
        return self.location.range

    def __str__(self):
        return self.name + "[" + self.kind + "]"

    def toDict(self):
        raise NotImplementedError()

    @staticmethod
    def fromDict(d: dict):
        try:
            return SymbolInformation(d["name"], SymbolKind(d["kind"]) if d["kind"] else None,
                                     d.get("deprecated"), Location.fromDict(d["location"]),
                                     d.get("containerName"))
        except Exception as ex:
            raise ValueError("Invalid input: {0}.".format(d)) from ex


class TextDocumentContentChangeEvent(LspContractObject):
    """
    An event describing a change to a text document. If range and rangeLength are omitted
    the new text is considered to be the full content of the document.
    """

    def __init__(self, text: str, range: Range = None, rangeLength: int = None):
        self.text = text
        self.range = range
        self.rangeLength = rangeLength

    def toDict(self):
        d = {"text": self.text}
        if self.range is not None:
            d["range"] = self.range
        if self.rangeLength is not None:
            d["rangeLength"] = self.rangeLength
        return d


class TextDocumentSaveReason(Enum):
    """
    Represents reasons why a text document is saved.
    """
    Manual = 1
    AfterDelay = 2
    FocusOut = 3


class FileChangeType(Enum):
    """The file event type."""
    Created = 1
    Changed = 2
    Deleted = 3


class FileEvent(LspContractObject):
    """
    An event describing a file change.
    """

    def __init__(self, uri: str, type: FileChangeType):
        self.uri = uri
        self.type = type

    def toDict(self):
        d = {"uri": self.uri, "type": self.type.value}
        return d


class Registration(LspContractObject):
    """
    Represents information about programming constructs like variables, classes,
    interfaces etc.
    """

    def __init__(self, id: str, method: str, registerOptions: dict):
        self.id = id
        self.method = method
        self.registerOptions = registerOptions

    def __str__(self):
        return self.id

    def toDict(self):
        raise NotImplementedError()

    @staticmethod
    def fromDict(d: dict):
        return Registration(d["id"], d["method"], d.get("registerOptions", None))
