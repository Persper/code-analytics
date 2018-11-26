"""
Contains CallGraphManager.
"""
import logging
from pathlib import Path
from typing import Iterable, NamedTuple, Tuple, Union

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
        #self.x = 0

    @property
    def graph(self):
        """
        Gets the underlying CallGraph.
        """
        return self._graph

    async def buildGraph(self, globPattern: Union[str, Iterable[str]] = None):
        """
        Build call graph branches from the specified files.

        globPattern: `str` or `str[]` containing the glob pattern of the files
        from which to build the call graph branches.
        """
        counter = 0
        async for branch in self._builder.buildCallGraphInFiles(globPattern):
            try:
                self._graph.add(branch)
                counter += 1
                if counter % 1000 == 0:
                    _logger.info("Already added %d branches.", counter)
            except ValueError as ex:
                _logger.debug("%s Branch: %s", ex, branch)
        _logger.info("Added %d branches.", counter)

    def removeByFiles(self, fileNames: Iterable[str]):
        """
        Clear the graph nodes whose source or definition node contains the specified files.
        """
        fileNames = set((Path(f).resolve() for f in fileNames))
        affectedFiles = set((i.sourceScope.file for i in self._graph.items if i.definitionScope.file in fileNames))
        affectedFiles.update(fileNames)
        self._graph.removeBySourceFiles(affectedFiles)

    async def rebuildGraph(self, fileNames: Iterable[str]):
        """
        Rebuild the source graph for the specified files. This operation will clear and rebuild the graph nodes
        whose source or definition node contains the specified files.
        """
        fileNames = set((Path(f).resolve() for f in fileNames))
        affectedFiles = set((i.sourceScope.file for i in self._graph.items if i.definitionScope.file in fileNames))
        affectedFiles.update(fileNames)
        self._graph.removeBySourceFiles(affectedFiles)
        #self.x += 1
        #self._graph.dumpTo("dmp" + str(self.x) + ".txt")
        await self.buildGraph((str(p) for p in affectedFiles))
