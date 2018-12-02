import asyncio
import logging
import subprocess
from abc import abstractclassmethod, abstractproperty
from pathlib import Path
from typing import List, Union

from persper.analytics.call_commit_graph import CallCommitGraph
from persper.analytics.graph_server import GraphServer
from persper.analytics.patch_parser import PatchParser

from .callgraph.adapters import CallCommitGraphSynchronizer
from .callgraph.builder import CallGraphBuilder
from .callgraph.manager import CallGraphManager
from .languageclient.lspclient import LspClient

_logger = logging.getLogger(__name__)


class LspClientGraphServer(GraphServer):

    defaultLanguageServerCommand: Union[str, List[str]] = None

    def __init__(self, workspaceRoot: str, languageServerCommand: Union[str, List[str]] = None):
        self._ccgraph = CallCommitGraph()
        self._callGraph = CallCommitGraphSynchronizer(self._ccgraph)
        self._workspaceRoot: Path = Path(workspaceRoot).resolve()
        self._invalidatedFiles = set()
        if not self._workspaceRoot.exists():
            self._workspaceRoot.touch()
        self._languageServerCommand = \
            languageServerCommand \
            if languageServerCommand != None \
            else type(self).defaultLanguageServerCommand
        self._lspServerProc: subprocess.Popen = None
        self._lspClient: LspClient = None
        self._callGraphBuilder: CallGraphBuilder = None
        self._callGraphManager: CallGraphManager = None

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

    async def end_commit(self, hexsha):
        await self.updateGraph()
        # self._callGraph.dumpTo("Graph-" + hexsha + ".txt")
        _logger.info("End commit: %s", hexsha)

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
