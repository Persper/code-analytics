import logging
import re
import urllib.parse
from abc import ABC, abstractclassmethod
from glob import iglob
from os import path
from pathlib import Path, PurePath
from typing import Dict, Iterable, List, Type, Union

from antlr4 import FileStream, Lexer, Token
from antlr4.error.ErrorListener import ErrorListener
from jsonrpc.exceptions import JsonRpcException

import wildcards
from persper.analytics.lsp_graph_server.languageclient.lspclient import LspClient
from persper.analytics.lsp_graph_server.languageclient.lspcontract import \
    DocumentSymbol, Location, Position, SymbolInformation, SymbolKind, \
    TextDocument, TextDocumentContentChangeEvent
from . import CallGraphBranch, CallGraphNode, CallGraphScope

_logger = logging.getLogger(__name__)

_KNOWN_EXTENSION_LANGUAGES = {
    ".h": "cpp",
    ".cpp": "cpp",
    ".hpp": "cpp",
    ".cc": "cpp",
    ".c": "c"
}


class TokenizedDocument:
    """
    Represents a fully tokenized document that supports finding a symbol or scope from
    the specified document position.
    """

    def __init__(self, tokens: Iterable[Token],
                 documentSymbols: Iterable[Union[DocumentSymbol, SymbolInformation]], fileName: PurePath):
        self._tokens = []
        self._scopes = []
        self._fileName = fileName
        # cquery returns SymbolInformation, which does not contain the exact position of the defined symbol.
        # We just assume symbol is at the first line of the container
        # DocumentSymbol
        # { (symbolLine, symbolColumn): symbolKind  }
        # SymbolInformation
        # { (symbolLine, symbolName): (containerColumn, symbolKind)  }
        symbolKinds = {}
        for s in documentSymbols:
            if isinstance(s, DocumentSymbol):
                # We assume selectionRange is exactly the range of symbol name
                symbolKinds[s.selectionRange.start.toTuple()] = s.kind
                self._scopes.append(CallGraphScope(s.name, s.kind, fileName, s.range.start, s.range.end))
            elif isinstance(s, SymbolInformation):
                symbolKinds[(s.location.range.start.line, s.name)] = (s.location.range.start.character, s.kind)
                self._scopes.append(CallGraphScope(s.containerName, s.kind, fileName,
                                                   s.location.range.start, s.location.range.end))
            else:
                _logger.error("Invalid DocumentSymbol in %s: %s", fileName, s)
        # put the scopes in document order of start positions, then by the document order of their end positions
        self._scopes.sort(key=lambda sc: (sc.startPos, sc.endPos))
        NOT_EXISTS = object()
        for t in tokens:
            t: Token
            assert t.line >= 1
            assert t.column >= 0
            line, col = t.line - 1, t.column
            kind = symbolKinds.pop((line, col), NOT_EXISTS)
            if kind is NOT_EXISTS:
                kind = symbolKinds.get((line, t.text))
                if kind:
                    containerCol, kind = kind
                    if containerCol <= col:
                        # Symbol must be in the container
                        # e.g.
                        # |container   |symbol      |container
                        # |starts here |starts here |ends here
                        # v            v            v
                        # int          main() { ... }
                        del symbolKinds[(line, t.text)]
                    else:
                        kind = None
            self._tokens.append(CallGraphNode(t.text, kind, fileName, Position(line, col), t.stop - t.start + 1))

    @property
    def tokens(self):
        return self._tokens

    @property
    def scopes(self):
        return self._scopes

    @property
    def fileName(self):
        return self._fileName

    def tokenAt(self, line: int, character: int) -> CallGraphNode:
        """
        Gets the CallGraphNode from the specified 0-base line and character position
        in the document.
        """
        L = 0
        R = len(self._tokens) - 1
        pos = Position(line, character)
        while L <= R:
            M = (L+R)//2
            tokenM: CallGraphNode = self._tokens[M]
            # assume there is no \n in token content
            endPos = Position(tokenM.pos.line, tokenM.pos.character + tokenM.length)
            if endPos <= pos:
                L = M + 1
            elif tokenM.pos > pos:
                R = M - 1
            else:
                return tokenM
        return None

    def scopeAt(self, line: int, character: int) -> CallGraphScope:
        """
        Gets the CallGraphScope from the specified 0-base line and character position
        in the document.
        """
        L = 0
        R = len(self._scopes) - 1
        MatchingM = None
        pos = Position(line, character)
        lastScope = None
        # Find the smallest container scope, assume the scopes do not intersect with each other
        # (either contains or not contains one another)
        for scope in self._scopes:
            # This is inefficient (yet correct)
            if scope.startPos > pos:
                break
            if pos < scope.endPos:
                if lastScope is None or lastScope.startPos <= scope.startPos <= lastScope.endPos:
                    lastScope = scope
        return lastScope


class CallGraphBuilder(ABC):
    """
    Building call graph branches from the given files with the specific Lexer and LspClient.
    """

    def __init__(self, lspClient: LspClient):
        if not isinstance(lspClient, LspClient):
            raise TypeError("lspClient should be an instance of LspClient.")
        self._lspClient = lspClient
        self._tokenizedDocCache: Dict[str, TokenizedDocument] = {}
        self._workspaceFilePatterns: List[str] = None
        self._workspaceFilePatternsRegex: list[re.Pattern] = None

    @property
    def lspClient(self):
        return self._lspClient

    # @lspClient.setter
    # def lspClient(self, value: LspClient):
    #     if not isinstance(value, LspClient):
    #         raise TypeError("lspClient should be an instance of LspClient.")
    #     self._lspClient = value

    @property
    def workspaceFilePatterns(self) -> List[str]:
        """
        A list of `str` containing the glob pattern of workspace files.
        When performing goto defintion operations, symbols defined ouside the workspace files
        will not be counted in as call graph branch.
        """
        return self._workspaceFilePatterns

    @workspaceFilePatterns.setter
    def workspaceFilePatterns(self, value: List[str]):
        self._workspaceFilePatterns = value
        if value:
            self._workspaceFilePatternsRegex = [re.compile(wildcards.translate(p)) for p in value]
        else:
            self._workspaceFilePatternsRegex = None

    def removeDocumentCache(self, path: Union[str, PurePath]):
        """
        Remove the lexer cache of a specified document by path.

        path: either be a `str` or a fully resolved `Path` instance.
        In the former case, the given path string will be resolved automatically.
        """
        if isinstance(path, str):
            path = Path(path).resolve()
        del self._tokenizedDocCache[path]

    async def getTokenizedDocument(self, path: Union[str, PurePath]):
        class MyLexerErrorListener(ErrorListener):
            def syntaxError(self, recognizer, offendingSymbol, line, column, msg, e):
                _logger.warning("%s:%d,%d: %s", path, line, column, msg)

        if isinstance(path, str):
            path = Path(path).resolve()
        doc = self._tokenizedDocCache.get(path)
        if doc:
            return doc
        textDoc = TextDocument.loadFile(path, self.inferLanguageId(path))
        input = FileStream(path, encoding="utf-8", errors="replace")
        lexer = self.createLexer(input)
        assert isinstance(lexer, Lexer)
        lexer.removeErrorListeners()
        lexer.addErrorListener(MyLexerErrorListener())
        documentSymbols = []
        if await self.openDocument(textDoc):
            try:
                documentSymbols = await self._lspClient.server.textDocumentGetSymbols(textDoc.uri)
            finally:
                # _logger.info("Close doc")
                self._lspClient.server.textDocumentDidClose(textDoc.uri)

        def tokenGenerator():
            while True:
                tk = lexer.nextToken()
                if tk.type == Token.EOF:
                    return
                if self.filterToken(tk):
                    yield tk
        doc = TokenizedDocument(tokenGenerator(), documentSymbols, path)
        self._tokenizedDocCache[path] = doc
        return doc

    def pathFromUri(self, expr: str) -> Path:
        expr: str = urllib.parse.unquote(expr).strip()
        if expr.lower().startswith("file:///"):
            expr = expr[8:]
        return Path(expr).resolve()

    @abstractclassmethod
    def filterToken(self, token: Token) -> bool:
        """
        When overridden in the derived class, determines whether the given token
        has the need to perform goto definition LSP invocations on.
        """
        raise NotImplementedError

    def filterFile(self, fileName: str):
        if self._workspaceFilePatternsRegex:
            return any(p.match(str(fileName)) for p in self._workspaceFilePatternsRegex)
        return True

    def inferLanguageId(self, path: PurePath) -> str:
        """
        Infers the language ID for the given document path.
        """
        ext = path.suffix.lower()
        return _KNOWN_EXTENSION_LANGUAGES[ext]
    
    @abstractclassmethod
    def createLexer(self, fileStream: FileStream) -> Lexer:
        raise NotImplementedError

    async def openDocument(self, textDoc: TextDocument):
        """
        Opens the specified text document, notifying the LSP server.
        """
        self._lspClient.server.textDocumentDidOpen(textDoc)

    async def closeDocument(self, uri: str):
        """
        Closes the specified text document, notifying the LSP server.

        uri: URI of the text document.
        """
        self._lspClient.server.textDocumentDidClose(uri)

    async def buildCallGraphInFiles(self, globPattern: Union[str, Iterable[str]] = None):
        """
        Build call graph branches asynchronously in files matching the specified glob pattern(s).
        """
        if not globPattern:
            if not self._workspaceFilePatterns:
                raise ValueError("globPattern is required if workspaceFilePatterns is not available.")
            globPattern = self._workspaceFilePatterns[0]
        if isinstance(globPattern, str):
            globPattern = [globPattern]
        visitedPaths = set()
        for pattern in globPattern:
            for fileName in iglob(pattern, recursive=True):
                if not path.isfile(fileName):
                    continue
                if fileName in visitedPaths:
                    continue
                visitedPaths.add(fileName)
                async for node in self.buildCallGraphInFile(fileName):
                    yield node

    async def buildCallGraphInFile(self, fileName: str) -> Iterable[CallGraphBranch]:
        """
        Build call graph branches asynchronously in the specified file.
        """
        srcPath = self.pathFromUri(fileName)
        _logger.info("Build call graph in: %s", srcPath)
        counter = 0
        thisDoc = await self.getTokenizedDocument(srcPath)
        textDoc = TextDocument.loadFile(srcPath, self.inferLanguageId(srcPath))
        if not await self.openDocument(textDoc):
            return
        try:
            for node in thisDoc.tokens:
                # Do not waste time on this
                if node.kind == SymbolKind.Namespace:
                    continue
                # Put the cursor to the middle.
                line, col = node.pos.line, node.pos.character + node.length//2
                _logger.debug(node)
                task = self._lspClient.server.textDocumentGotoDefinition(textDoc.uri, (line, col))
                nodeScope = thisDoc.scopeAt(line, col)
                defs = await task
                defNodes = []
                for d in defs:
                    d: Location
                    defPath = self.pathFromUri(d.uri)
                    if not self.filterFile(defPath):
                        continue
                    defsDoc = await self.getTokenizedDocument(defPath)
                    defNode = defsDoc.tokenAt(d.range.start.line, d.range.start.character)
                    defScope = defsDoc.scopeAt(d.range.start.line, d.range.start.character)
                    if not defNode:
                        # Failed to retrieve a node from the given position.
                        _logger.warning("Failed to retrieve node from %s:%s.", defPath, d.range)
                        defNode = CallGraphNode(None, None, defPath, d.range.start, None)
                    if defNode == node:
                        # This node itself is a definition. Do not waste time on this.
                        defNodes = None
                        break
                    if defNode.kind == SymbolKind.Namespace:
                        # Find some namespace. Do not waste time on this.
                        defNodes = None
                        break
                    defNodes.append((defNode, defScope))
                if defNodes:
                    for dn, ds in defNodes:
                        counter += 1
                        yield CallGraphBranch(nodeScope, ds, node, dn)
        finally:
            await self.closeDocument(textDoc.uri)
        _logger.info("Yielded %d branches.", counter)

    async def deleteFile(self, fileName: str):
        path = Path(fileName).resolve()
        if not path.exists:
            return False
        self.removeDocumentCache(path)
        doc = TextDocument(TextDocument.fileNameToUri(str(path)), self.inferLanguageId(path), 1, "")
        self._lspClient.server.textDocumentDidOpen(doc)
        # Empty the file and notify language server.
        self._lspClient.server.textDocumentDidChange(doc.uri, 2, [TextDocumentContentChangeEvent("")])
        path.unlink()
        self._lspClient.server.textDocumentDidSave(doc.uri)
        await self.closeDocument(doc.uri)

    async def modifyFile(self, fileName: str, newContent: str):
        """
        Modify a file's content, notifying the language server, as if the file
        is modified in the editor.
        """
        if newContent is None:
            newContent = ""
        path = Path(fileName).resolve()
        try:
            doc = TextDocument.loadFile(str(path), self.inferLanguageId(path), 1) \
                if path.exists() \
                else TextDocument(TextDocument.fileNameToUri(str(path)), self.inferLanguageId(path), 1, "")
            try:
                self.removeDocumentCache(path)
                self._lspClient.server.textDocumentDidOpen(doc)
                self._lspClient.server.textDocumentDidChange(doc.uri, 2, [TextDocumentContentChangeEvent(newContent)])
                with open(fileName, "wt", encoding="utf-8") as f:
                    f.write(newContent)
                self._lspClient.server.textDocumentDidSave(doc.uri)
                _logger.info("Modified %s.", path)
                return doc.text
            finally:
                await self.closeDocument(doc.uri)
        except Exception as ex:
            raise Exception("Cannot modify {0}.".format(path)) from ex
