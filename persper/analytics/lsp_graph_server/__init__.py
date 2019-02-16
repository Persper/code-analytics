import asyncio
import logging
import os
import subprocess
from abc import abstractclassmethod, abstractproperty
from datetime import datetime, timedelta
from os import path
from pathlib import Path, PurePath
from typing import Dict, List, Tuple, Union

from persper.analytics.call_commit_graph import CallCommitGraph
from persper.analytics.graph_server import GraphServer, CommitSeekingMode
from persper.analytics.another_patch_parser import parseUnifiedDiff

from .callgraph import CallGraphScope
from .callgraph.adapters import CallCommitGraphSynchronizer
from .callgraph.builder import CallGraphBuilder, TokenizedDocument
from .callgraph.manager import CallGraphManager
from .languageclient.lspclient import LspClient

_logger = logging.getLogger(__name__)


class LspClientGraphServer(GraphServer):
    """
    The common base class for LSP-client backed-up call graph server.

    The derived class of this class should be used with `async with` statement:
    ```
    async with LspClientGraphServer(..) as graphServer:
        ...
    ```
    """
    defaultLanguageServerCommand: Union[str, List[str]] = None
    defaultLoggedLanguageServerCommand: Union[str, List[str]] = None

    def __init__(self, workspaceRoot: str,
                 languageServerCommand: Union[str, List[str]] = None,
                 dumpLogs: bool = False,
                 dumpGraphs: bool = False,
                 graph: CallCommitGraph = None):
        """
        workspaceRoot:  root of the temporary workspace path. LSP workspace and intermediate repository files
        will be placed in this folder.

        languageServerCommand: the command line (in string, or a sequence of parameters) for starting the
        language server process. If use `null` or default value,
        the value of current class's `defaultLanguageServerCommand` static field will be used.
        """
        self._ccgraph = graph or CallCommitGraph()
        self._callGraph = CallCommitGraphSynchronizer(self._ccgraph)
        self._workspaceRoot: Path = Path(workspaceRoot).resolve()
        self._invalidatedFiles = set()
        if not self._workspaceRoot.exists():
            self._workspaceRoot.touch()
        if languageServerCommand:
            self._languageServerCommand = languageServerCommand
        elif dumpLogs and type(self).defaultLoggedLanguageServerCommand:
            self._languageServerCommand = type(self).defaultLoggedLanguageServerCommand
        else:
            self._languageServerCommand = type(self).defaultLanguageServerCommand
        self._lspServerProc: subprocess.Popen = None
        self._lspClient: LspClient = None
        self._callGraphBuilder: CallGraphBuilder = None
        self._callGraphManager: CallGraphManager = None
        self._lastFileWrittenTime: datetime = None
        self._dumpLogs = dumpLogs
        self._dumpGraphs = dumpGraphs
        # [(oldPath, newPath, addedLines, removedLines), ...]
        # added/removedLines := [[startLine, modifiedLines], ...]
        self._stashedPatches: List[Tuple[PurePath, PurePath, List[Tuple[int, int]], List[Tuple[int, int]]]] = []
        self._commitSeekingMode: CommitSeekingMode = None

    def __getstate__(self):
        state = self.__dict__.copy()
        state.pop("_lspServerProc", None)
        state.pop("_lspClient", None)
        state.pop("_callGraphBuilder", None)
        state.pop("_callGraphManager", None)
        return state

    def __setstate__(self, state):
        self.__dict__.update(state)
        if not self._workspaceRoot.exists():
            self._workspaceRoot.touch()

    def start_commit(self, hexsha: str, seeking_mode: CommitSeekingMode, author_name: str,
                     author_email: str, commit_message: str):
        self._commitSeekingMode = seeking_mode
        if seeking_mode != CommitSeekingMode.Rewind:
            self._ccgraph.add_commit(hexsha, author_name, author_email, commit_message)

    async def update_graph(self, old_filename: str, old_src: str, new_filename: str, new_src: str, patch: bytes):
        oldPath = self._workspaceRoot.joinpath(old_filename).resolve() if old_filename else None
        newPath = self._workspaceRoot.joinpath(new_filename).resolve() if new_filename else None
        assert oldPath or newPath

        # update node history
        if self._commitSeekingMode == CommitSeekingMode.NormalForward:
            if newPath is None:
                # The file has been deleted
                # We need to scan it before it's gone, instead of in end_commit
                self._markWholeDocumentAsChanged(await self._callGraphBuilder.getTokenizedDocument(oldPath))
            elif oldPath is None:
                # The file has been added
                self._stashedPatches.append((oldPath, newPath, None, None))
            else:
                added, removed = parseUnifiedDiff(patch.decode('utf-8', 'replace'))
                # calculate removed lines
                if removed:
                    # we can have removed lines only when we have old file
                    oldDoc: TokenizedDocument = await self._callGraphBuilder.getTokenizedDocument(oldPath)
                    # start, end are inclusive, 1-based
                    for start, end in removed:
                        for i in range(start - 1, end):
                            scope = oldDoc.scopeAt(i, 0)
                            if scope:
                                self._safeUpdateNodeHistory(scope.name, 1)
                self._stashedPatches.append((oldPath, newPath, added, None))

        # perform file operations
        if oldPath and oldPath != newPath:
            # The file has been moved/deleted
            await self._callGraphBuilder.deleteFile(oldPath)
            self._invalidatedFiles.add(oldPath)
        if newPath:
            # The file has been created/modified
            await self._callGraphBuilder.modifyFile(newPath, new_src)
            self._invalidatedFiles.add(newPath)
        self._lastFileWrittenTime = datetime.now()

    def _safeUpdateNodeHistory(self, name: str, changeOfLines: int):
        if name not in self._ccgraph.nodes():
            self._ccgraph.add_node(name)
        self._ccgraph.update_node_history(name, changeOfLines)

    def _markWholeDocumentAsChanged(self, doc: TokenizedDocument):
        parentScopes = []
        # print("_markWholeDocumentAsChanged: ", doc.fileName)
        for scope in doc.scopes:
            while parentScopes and parentScopes[-1][0].endPos <= scope.startPos:
                # scope is out of parentScope, then the changed line count for parentScope is decided
                s, c = parentScopes.pop()
                self._safeUpdateNodeHistory(s.name, c)
            thisScopeLines = scope.endPos.line - scope.startPos.line + 1
            if parentScopes:
                # Subtract LOC from innermost scope to eliminate dups
                innermostScope = parentScopes[-1]
                s, c = innermostScope
                assert s.startPos <= scope.startPos and s.endPos >= scope.endPos, \
                    "`scope` should be inside parent scope: {0}. parentScopes: {1}".format(s, parentScopes)
                c -= thisScopeLines
                # If there are more than 1 scope on the same line,
                # we will count in 1 line for each scope
                if s.startPos.line == scope.startPos.line:
                    c += 1
                if s.startPos.line < s.endPos.line == scope.endPos.line:
                    c += 1
                assert c >= 0, \
                    "parentScope's LOC change is negative: {0}. parentScopes: {1}".format(s, parentScopes)
                innermostScope[1] = c
            parentScopes.append([scope, thisScopeLines])
        while parentScopes:
            s, c = parentScopes.pop()
            self._safeUpdateNodeHistory(s.name, c)

    async def end_commit(self, hexsha):
        # update vetices & edges
        if self._commitSeekingMode != CommitSeekingMode.Rewind:
            await self.updateGraph()
            if self._dumpGraphs:
                self._callGraph.dumpTo("Graph-" + hexsha + ".txt")

        # calculate added lines
        if self._commitSeekingMode == CommitSeekingMode.NormalForward:
            for oldPath, newPath, added, _ in self._stashedPatches:
                if not newPath:
                    continue
                if oldPath and not added:
                    continue
                newDoc: TokenizedDocument = await self._callGraphBuilder.getTokenizedDocument(newPath)
                if not oldPath:
                    # file has been added
                    self._markWholeDocumentAsChanged(newDoc)
                else:
                    assert added
                    for start, end in added:
                        for i in range(start - 1, end):
                            scope = newDoc.scopeAt(i, 0)
                            if scope:
                                self._safeUpdateNodeHistory(scope.name, 1)
        self._stashedPatches.clear()

        # ensure the files in the next commit has a different timestamp from this commit.
        if datetime.now() - self._lastFileWrittenTime < timedelta(seconds=1):
            await asyncio.sleep(1)

    def get_graph(self):
        return self._ccgraph

    def reset_graph(self):
        self._callGraph.clear()

    def filter_file(self, filename):
        filePath = self._workspaceRoot.joinpath(filename).resolve()
        # _logger.info("Filter: %s -> %s", filePath, self._callGraphBuilder.filterFile(str(filePath)))
        return self._callGraphBuilder.filterFile(str(filePath))

    def config(self, param: dict):
        pass

    async def __aenter__(self):
        await self.startLspClient()
        return self

    async def __aexit__(self, exc_type, exc_value, traceback):
        await self.stopLspClient()

    async def startLspClient(self):
        """
        When overridden in derived class, starts the LSP server process,
        and sets the following fields properly:
        * self._lspServerProc
        * self._lspClient
        * self._callGraphBuilder
        * self._callGraphManager
        """
        if os.name == "nt":
            self._lspServerProc = subprocess.Popen(
                self._languageServerCommand,
                stdin=subprocess.PIPE,
                stdout=subprocess.PIPE,
                creationflags=subprocess.CREATE_NEW_CONSOLE)
        else:
            self._lspServerProc = subprocess.Popen(
                self._languageServerCommand,
                stdin=subprocess.PIPE,
                stdout=subprocess.PIPE,
                shell=True)

    async def stopLspClient(self):
        """
        Performs LSP client stop sequence.
        This method is usually invoked in `__aexit__` so you do not have to call it manually
        if you are using this class instance with `async with` statement.
        """
        if not self._lspServerProc:
            return
        _logger.info("Shutting down language server...")
        await asyncio.wait_for(self._lspClient.server.shutdown(), 10)
        self._lspClient.server.exit()
        try:
            exitCode = self._lspServerProc.wait(10)
            _logger.info("Language server %d exited with code: %s.", self._lspServerProc.pid, exitCode)
        except subprocess.TimeoutExpired:
            self._lspServerProc.kill()
            _logger.warning("Killed language server %d.", self._lspServerProc.pid)
        self._lspServerProc = None
        self._callGraphBuilder = None
        self._callGraphManager = None

    def invalidateFile(self, path: Union[str, Path]):
        """
        Mark the call graph for the specified file as invalidated, so it should be re-generated in
        the next `updateGraph` call.
        """
        if isinstance(path, str):
            path = Path(path).resolve()
        self._invalidatedFiles.add(path)

    async def updateGraph(self):
        if not self._invalidatedFiles:
            return
        affectedFiles = self._callGraphManager.removeByFiles(self._invalidatedFiles)
        _logger.info("Invalidated %d files, affected %d files.", len(self._invalidatedFiles), len(affectedFiles))
        await self._callGraphBuilder.waitForFileSystem()
        # update vertices
        # Use scope full name as identifier.
        for path in affectedFiles:
            path: Path
            if not path.exists():
                continue
            for scope in await self._callGraphBuilder.enumScopesInFile(str(path)):
                scope: CallGraphScope
                if scope.name not in self._ccgraph.nodes().data():
                    self._ccgraph.add_node(scope.name)
        # update edges
        await self._callGraphManager.buildGraph(fileNames=affectedFiles)
        self._invalidatedFiles.clear()
