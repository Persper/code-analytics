import asyncio
import logging
import subprocess
from abc import abstractclassmethod, abstractproperty
from pathlib import Path
from typing import List, Union
from datetime import datetime, timedelta

from persper.analytics.call_commit_graph import CallCommitGraph
from persper.analytics.graph_server import GraphServer
from persper.analytics.patch_parser import PatchParser

from .callgraph.adapters import CallCommitGraphSynchronizer
from .callgraph.builder import CallGraphBuilder
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
                 dumpGraphs: bool = False):
        """
        workspaceRoot:  root of the temporary workspace path. LSP workspace and intermediate repository files
        will be placed in this folder.

        languageServerCommand: the command line (in string, or a sequence of parameters) for starting the
        language server process. If use `null` or default value,
        the value of current class's `defaultLanguageServerCommand` static field will be used.
        """
        self._ccgraph = CallCommitGraph()
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

    def __getstate__(self):
        state = self.__dict__.copy()
        del state["_lspServerProc"]
        del state["_lspClient"]
        del state["_callGraphBuilder"]
        del state["_callGraphManager"]

    def __setstate__(self, state):
        self.__dict__.update(state)
        if not self._workspaceRoot.exists():
            self._workspaceRoot.touch()

    def register_commit(self, hexsha, author_name, author_email, commit_message):
        self._ccgraph.add_commit(hexsha, author_name, author_email, commit_message)

    async def update_graph(self, old_filename: str, old_src: str, new_filename: str, new_src: str, patch: bytes):
        oldPath = self._workspaceRoot.joinpath(old_filename).resolve() if old_filename else None
        newPath = self._workspaceRoot.joinpath(new_filename).resolve() if new_filename else None
        assert oldPath or newPath
        if oldPath and oldPath != newPath:
            await self._callGraphBuilder.deleteFile(oldPath)
            self._invalidatedFiles.add(oldPath)
        if newPath:
            await self._callGraphBuilder.modifyFile(newPath, new_src)
            self._invalidatedFiles.add(newPath)
        self._lastFileWrittenTime = datetime.now()

    async def end_commit(self, hexsha):
        await self.updateGraph()
        if self._dumpGraphs:
            self._callGraph.dumpTo("Graph-" + hexsha + ".txt")
        _logger.info("End commit: %s", hexsha)
        # ensure the files in the next commit has a different timestamp as this commit.
        if datetime.now() - self._lastFileWrittenTime < timedelta(seconds=1):
            await asyncio.sleep(1)

    async def get_graph(self):
        return self._ccgraph

    def reset_graph(self):
        self._callGraph.clear()

    def filter_file(self, filename):
        filePath = self._workspaceRoot.joinpath(filename).resolve()
        # print("Filter: ", filePath, self._callGraphBuilder.filterFile(str(filePath)))
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
        self._lspServerProc = subprocess.Popen(
            self._languageServerCommand,
            stdin=subprocess.PIPE, stdout=subprocess.PIPE,
            creationflags=subprocess.CREATE_NEW_CONSOLE)

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
        exitCode = self._lspServerProc.wait(10)
        if exitCode != None:
            _logger.info("Language server %d exited with code: %s.", self._lspServerProc.pid, exitCode)
        else:
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
        await self._callGraphManager.buildGraph(fileNames=affectedFiles)
        self._invalidatedFiles.clear()
