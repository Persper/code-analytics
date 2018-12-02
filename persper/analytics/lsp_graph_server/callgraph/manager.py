"""
Contains CallGraphManager.
"""
import logging
from pathlib import Path, PurePath
from typing import Iterable, NamedTuple, Tuple, Union
from os import path

from . import CallGraph
from .builder import CallGraphBuilder

_logger = logging.getLogger(__name__)


class CallGraphManager():
    """
    Used to construct / update call graph independently of specific implementations of
    CallGraphBuilder.
    """

    def __init__(self, builder: CallGraphBuilder, callGraph: CallGraph = None):
        if not isinstance(builder, CallGraphBuilder):
            raise TypeError("builderType should be a subtype of CallGraphBuilder.")
        self._builder = builder
        self._graph = callGraph or CallGraph()
        # self._rebuildCounter = 0

    @property
    def graph(self):
        """
        Gets the underlying CallGraph.
        """
        return self._graph

    async def buildGraph(self, fileNames: Union[str, Iterable[str]] = None, globPattern: Union[str, Iterable[str]] = None):
        """
        Build call graph branches from the specified files.

        globPattern: `str` or `str[]` containing the glob pattern of the files
        from which to build the call graph branches.
        """
        counter = 0

        def pushBranch(branch):
            nonlocal counter
            try:
                self._graph.add(branch)
                counter += 1
                if counter % 1000 == 0:
                    _logger.info("Already added %d branches.", counter)
            except ValueError as ex:
                _logger.debug("%s Branch: %s", ex, branch)

        if fileNames:
            if isinstance(fileNames, (str, PurePath)):
                fileNames = [fileNames]
            for fn in fileNames:
                sfn = str(fn)
                if not path.exists(sfn):
                    continue
                async for b in self._builder.buildCallGraphInFile(sfn):
                    pushBranch(b)
        if globPattern or not fileNames:
            async for b in self._builder.buildCallGraphInFiles(globPattern):
                pushBranch(b)
        _logger.info("Added %d branches.", counter)

    def removeByFiles(self, fileNames: Iterable[str]) -> Iterable[Path]:
        """
        Clear the graph nodes whose source or definition node contains the specified files.
        """
        fileNames = set((Path(f).resolve() for f in fileNames))
        affectedFiles = set((i.sourceScope.file for i in self._graph.items if i.definitionScope.file in fileNames))
        affectedFiles.update(fileNames)
        self._graph.removeBySourceFiles(affectedFiles)
        return affectedFiles

    async def rebuildGraph(self, fileNames: Iterable[str]):
        """
        Rebuild the source graph for the specified files. This operation will clear and rebuild the graph nodes
        whose source or definition node contains the specified files.
        """
        affectedFiles = self.removeByFiles(fileNames)
        self._rebuildCounter += 1
        # self._graph.dumpTo("rebuild_" + str(self._rebuildCounter) + ".txt")
        await self.buildGraph((str(p) for p in affectedFiles))
