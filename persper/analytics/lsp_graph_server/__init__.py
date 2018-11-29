from persper.analytics.patch_parser import PatchParser
from persper.analytics.graph_server import GraphServer
from persper.analytics.call_commit_graph import CallCommitGraph
from abc import abstractclassmethod, abstractproperty
from .languageclient.lspclient import LspClient
from .callgraph.manager import CallGraphManager
from .callgraph.builder import CallGraphBuilder
from pathlib import Path
from typing import Union
import asyncio


class LspClientGraphServer(GraphServer):
    def __init__(self, workspaceRoot: str):
        self._ccgraph = CallCommitGraph()
        self._workspaceRoot: Path = Path(workspaceRoot).resolve()
        self._invalidatedFiles = set()
        self._loop = asyncio.new_event_loop()
        if not self._workspaceRoot.exists():
            self._workspaceRoot.touch()

    def register_commit(self, hexsha, author_name, author_email, commit_message):
        self._ccgraph.add_commit(hexsha, author_name, author_email, commit_message)

    def update_graph(self, old_filename: str, old_src: str, new_filename: str, new_src: str, patch: bytes):
        self._loop.run_until_complete(self.onFileChanged(old_filename, old_src, new_filename, new_src, patch))

    async def onFileChanged(self, old_filename: str, old_src: str, new_filename: str, new_src: str, patch: bytes):
        oldPath = self._workspaceRoot.joinpath(old_filename).resolve() if old_filename else None
        newPath = self._workspaceRoot.joinpath(new_filename).resolve() if new_filename else None
        if old_filename != new_filename:
            await self._callGraphBuilder.deleteFile(oldPath)
            await self._callGraphBuilder.modifyFile(new_filename, new_src)
        self._invalidatedFiles.add(oldPath)
        self._invalidatedFiles.add(newPath)

    def get_graph(self):
        self._loop.run_until_complete(self.updateGraph())
        

    def reset_graph(self):
        self._callGraphManager.graph.clear()

    def filter_file(self, filename):
        pass

    def config(self, param: dict):
        pass

    @abstractclassmethod
    async def startLspClient(self):
        raise NotImplementedError()

    @abstractclassmethod
    async def _stopLspClient(self):
        raise NotImplementedError()

    @abstractproperty
    def _lspClient(self) -> LspClient:
        raise NotImplementedError()

    @abstractproperty
    def _callGraphBuilder(self) -> CallGraphBuilder:
        raise NotImplementedError()

    @abstractproperty
    def _callGraphManager(self) -> CallGraphManager:
        raise NotImplementedError()

    def invalidateFile(self, path: Union[str, Path]):
        if isinstance(path, str):
            path = Path(path).resolve()
        self._invalidatedFiles.add(path)

    async def updateGraph(self):
        affectedFiles = self._callGraphManager.removeByFiles(self._invalidatedFiles)
        self._callGraphManager.buildGraph(fileNames=affectedFiles)
        self._invalidatedFiles.clear()
