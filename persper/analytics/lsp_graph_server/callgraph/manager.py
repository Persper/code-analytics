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
        branchCounter = 0       # with dups
        fileCounter = 0
        await self._builder.waitForFileSystem()

        def pushBranch(branch):
            nonlocal branchCounter
            try:
                self._graph.add(branch)
                branchCounter += 1
                if branchCounter % 2000 == 0:
                    _logger.debug("Already added %d branches.", branchCounter)
            except ValueError as ex:
                _logger.warn("%s Branch: %s", ex, branch)

        if fileNames:
            if isinstance(fileNames, (str, PurePath)):
                fileNames = [fileNames]
            for fn in fileNames:
                sfn = str(fn)
                if not path.exists(sfn):
                    continue
                fileCounter += 1
                async for b in self._builder.buildCallGraphInFile(sfn):
                    pushBranch(b)
        if globPattern or not fileNames:
            async for b in self._builder.buildCallGraphInFiles(globPattern):
                pushBranch(b)
        if fileNames and not globPattern:
            _logger.debug("Added %d branches from %d files.", branchCounter, fileCounter)
        else:
            _logger.debug("Added %d branches.", branchCounter)

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
        # self._rebuildCounter += 1
        # self._graph.dumpTo("rebuild_" + str(self._rebuildCounter) + ".txt")
        await self.buildGraph((str(p) for p in affectedFiles))
