"""
ccls client-side LSP support.
"""
import logging
import os
import time
from asyncio import sleep
from pathlib import Path, PurePath
from typing import List, Union

from antlr4 import Token
from antlr4.FileStream import FileStream
from jsonrpc.endpoint import Endpoint
from jsonrpc.exceptions import JsonRpcException

from persper.analytics.call_commit_graph import CallCommitGraph

from . import LspClientGraphServer
from .callgraph.builder import CallGraphBuilder
from .callgraph.manager import CallGraphManager
from .fileparsers.CPP14Lexer import CPP14Lexer
from .languageclient.lspclient import LspClient
from .languageclient.lspcontract import LspContractObject, TextDocument, TextDocumentContentChangeEvent
from .languageclient.lspserver import LspServerStub

_logger = logging.getLogger(__name__)


class CclsInfo(LspContractObject):
    def __init__(self, pendingIndexRequests: int, postIndexWorkItems: int, projectEntries: int):
        self.pendingIndexRequests = pendingIndexRequests
        self.postIndexWorkItems = postIndexWorkItems
        self.projectEntries = projectEntries

    def toDict(self):
        raise NotImplementedError()

    @staticmethod
    def fromDict(d: dict):
        return CclsInfo(int(d["pipeline"]["pendingIndexRequests"]),
                        0,
                        int(d["project"]["entries"]))


class CclsLspServerStub(LspServerStub):
    def __init__(self, endpoint: Endpoint):
        super().__init__(endpoint)

    def textDocumentGetSymbols(self, *args, **kwargs):
        if kwargs == None:
            kwargs = {}
        if "requestParamsOverride" not in kwargs:
            kwargs["requestParamsOverride"] = {}
        return super().textDocumentGetSymbols(*args, **kwargs)

    async def cclsInfo(self):
        """
        Gets the ccls language server status.
        """
        result = await self.request("$ccls/info")
        return CclsInfo.fromDict(result)


class CclsLspClient(LspClient):
    def __init__(self, rx, tx, logFile: str = None):
        super().__init__(rx, tx, logFile)
        self._serverStub = CclsLspServerStub(self._endpoint)

    def m_ccls__publish_skipped_ranges(self, uri: str, skippedRanges: list):
        pass

    def m_ccls__publish_semantic_highlight(self, uri: str, symbols: list):
        pass


class CclsCallGraphBuilder(CallGraphBuilder):
    # Do not F12 on operators. cquery tend to randomly jump to false-positives for non-overloaded operators.
    _tokensOfInterest = {CPP14Lexer.Identifier,
                         #  CPP14Lexer.Plus,
                         #  CPP14Lexer.Minus,
                         #  CPP14Lexer.Star,
                         #  CPP14Lexer.Div,
                         #  CPP14Lexer.Mod,
                         #  CPP14Lexer.Caret,
                         #  CPP14Lexer.And,
                         #  CPP14Lexer.Or,
                         #  CPP14Lexer.Tilde,
                         #  CPP14Lexer.Not,
                         #  CPP14Lexer.Assign,
                         #  CPP14Lexer.Less,
                         #  CPP14Lexer.Greater,
                         #  CPP14Lexer.PlusAssign,
                         #  CPP14Lexer.MinusAssign,
                         #  CPP14Lexer.StarAssign,
                         #  CPP14Lexer.DivAssign,
                         #  CPP14Lexer.ModAssign,
                         #  CPP14Lexer.XorAssign,
                         #  CPP14Lexer.AndAssign,
                         #  CPP14Lexer.OrAssign,
                         #  CPP14Lexer.LeftShift,
                         #  CPP14Lexer.LeftShiftAssign,
                         #  CPP14Lexer.Equal,
                         #  CPP14Lexer.NotEqual,
                         #  CPP14Lexer.LessEqual,
                         #  CPP14Lexer.GreaterEqual,
                         #  CPP14Lexer.AndAnd,
                         #  CPP14Lexer.OrOr,
                         #  CPP14Lexer.PlusPlus,
                         #  CPP14Lexer.MinusMinus
                         }

    def __init__(self, lspClient: CclsLspClient):
        if not isinstance(lspClient, CclsLspClient):
            raise TypeError("lspClient should be an instance of CclsLspClient.")
        super().__init__(lspClient)
        self._lspClient: CclsLspClient
        self._openDocumentWaitDuration = 0

    def createLexer(self, fileStream: FileStream):
        return CPP14Lexer(fileStream)

    def filterToken(self, token: Token):
        return token.type in self._tokensOfInterest

    def inferLanguageId(self, path: PurePath):
        return "cpp"

    def modifyFile(self, fileName: str, newContent: str):
        return super().modifyFile(fileName, newContent)

    async def _waitForJobs(self):
        lastJobs = None
        while True:
            info: CclsInfo = await self._lspClient.server.cclsInfo()
            curJobs = info.pendingIndexRequests + info.postIndexWorkItems
            if curJobs != lastJobs:
                _logger.debug("Server jobs: %d.", curJobs)
                lastJobs = curJobs
            if curJobs == 0:
                break
            if curJobs < 5:
                await sleep(0.05)
            elif curJobs < 50:
                await sleep(0.1)
            else:
                await sleep(1)

    async def openDocument(self, textDoc: TextDocument):
        self._lspClient.server.textDocumentDidOpen(textDoc)
        t1 = time.monotonic()
        while True:
            try:
                await self._waitForJobs()
                self._openDocumentWaitDuration += time.monotonic() - t1
                return True
            except JsonRpcException as ex:
                if ex.code == -32002:
                    _logger.warning("Language server is not ready. Waiting…")
                    await sleep(5)
                elif ex.code == -32603 and "unable to find" in ex.message:
                    _logger.warning("The file seems invalid. Server error: %s", ex.message)
                    return False
                raise

    def logOpenDocumentWaitDuration(self):
        _logger.info("openDocument waitForJobs takes %.2f s.", self._openDocumentWaitDuration)
        self._openDocumentWaitDuration = 0


class CclsGraphServer(LspClientGraphServer):

    defaultLanguageServerCommand = "./bin/ccls"
    defaultLoggedLanguageServerCommand = "./bin/ccls -log-file=ccls.log"

    def __init__(self, workspaceRoot: str, cacheRoot: str = None,
                 languageServerCommand: Union[str, List[str]] = None,
                 dumpLogs: bool = False,
                 graph: CallCommitGraph = None):
        super().__init__(workspaceRoot, languageServerCommand=languageServerCommand,
                         dumpLogs=dumpLogs, graph=graph)
        if cacheRoot == True:
            cacheRoot = self._workspaceRoot.joinpath(".ccls-cache")
        self._cacheRoot = Path(cacheRoot).resolve() if cacheRoot else None
        self._c_requireScopeDefinitionMatch = True

    async def startLspClient(self):
        await super().startLspClient()
        self._lspClient = CclsLspClient(self._lspServerProc.stdout, self._lspServerProc.stdin,
                                        logFile="rpclog.log" if self._dumpLogs else None)
        self._lspClient.start()
        _logger.debug(await self._lspClient.server.initialize(
            rootFolder=self._workspaceRoot,
            initializationOptions={"cacheDirectory": str(self._cacheRoot),
                                   "diagnostics": {"onParse": False, "onType": False},
                                   "discoverSystemIncludes": True,
                                   "enableCacheRead": self._cacheRoot != None,
                                   "enableCacheWrite": self._cacheRoot != None,
                                   "clang": {
                                       "excludeArgs": [],
                                       "extraArgs": [
                                           "-nocudalib",
                                           "-fno-delayed-template-parsing"      # fix for not parsing templates on windows-msvc
                                       ],
                                       "pathMappings": [],
                                       "resourceDir": ""
            },
                "index": {"threads": 0}
            }))
        self._lspClient.server.initialized()
        self._callGraphBuilder = CclsCallGraphBuilder(self._lspClient)
        self._callGraphBuilder.workspaceFilePatterns = [
            str(self._workspaceRoot.joinpath("**/*.[Hh]")),
            str(self._workspaceRoot.joinpath("**/*.[Hh][Hh]")),
            str(self._workspaceRoot.joinpath("**/*.[Hh][Pp][Pp]")),
            str(self._workspaceRoot.joinpath("**/*.[Cc]")),
            str(self._workspaceRoot.joinpath("**/*.[Cc][Cc]")),
            str(self._workspaceRoot.joinpath("**/*.[Cc][Pp][Pp]")),
            str(self._workspaceRoot.joinpath("**/*.[Cc][Xx][Xx]"))
        ]
        self._callGraphManager = CallGraphManager(self._callGraphBuilder, self._callGraph)

    def _orderAffectedFiles(self, paths: List[Path]):
        # put cpp files ahead of h files to ensure h files are parsed correctly (e.g. stdafx.h/pch.h)
        otherFiles = []
        for p in paths:
            p: Path
            if p.name.endswith(".c") or p.name.endswith(".cc") or p.name.endswith(".cpp"):
                yield p
            else:
                otherFiles.append(p)
        for p in otherFiles:
            yield p

    async def end_commit(self, hexsha: str):
        try:
            await super().end_commit(hexsha)
        finally:
            self._callGraphBuilder.logOpenDocumentWaitDuration()
