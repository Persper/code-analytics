"""
ccls client-side LSP support.
"""
import logging
from asyncio import sleep
from pathlib import Path, PurePath
from typing import List, Union

from antlr4 import Token
from antlr4.FileStream import FileStream
from jsonrpc.endpoint import Endpoint
from jsonrpc.exceptions import JsonRpcException

from . import LspClientGraphServer
from .callgraph.builder import CallGraphBuilder
from .callgraph.manager import CallGraphManager
from .fileparsers.CPP14Lexer import CPP14Lexer
from .languageclient.lspclient import LspClient
from .languageclient.lspcontract import TextDocument
from .languageclient.lspserver import LspServerStub

_logger = logging.getLogger(__name__)


class CclsLspServerStub(LspServerStub):
    def __init__(self, endpoint: Endpoint):
        super().__init__(endpoint)

    async def getJobs(self):
        """
        Gets the count of jobs to be done before server can provide latest call information.
        """
        result = await self.request("$ccls/getJobs")
        return int(result)


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
        super().__init__(CPP14Lexer, lspClient)

    def createLexer(self, fileStream: FileStream):
        return CPP14Lexer(fileStream)

    def filterToken(self, token: Token):
        return token.type in self._tokensOfInterest

    def inferLanguageId(self, path: PurePath):
        return "cpp"

    def modifyFile(self, fileName: str, newContent: str):
        return super().modifyFile(fileName, newContent)

    async def openDocument(self, textDoc: TextDocument):
        self._lspClient.server.textDocumentDidOpen(textDoc)
        lastJobs = None
        while True:
            try:
                while True:
                    curJobs = await self._lspClient.server.getJobs()
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
                # dummy request
                await self._lspClient.server.textDocumentCodeLens(textDoc.uri)
                return True
            except JsonRpcException as ex:
                if ex.code == -32002:
                    _logger.warning("Language server is not ready. Waiting…")
                    await sleep(5)
                elif ex.code == -32603 and "unable to find" in ex.message:
                    _logger.warning("The file seems invalid. Server error: %s", ex.message)
                    return False
                raise


class CclsGraphServer(LspClientGraphServer):

    defaultLanguageServerCommand = "./bin/ccls -log-file=ccls.log"

    def __init__(self, workspaceRoot: str, cacheRoot: str = None, languageServerCommand: Union[str, List[str]] = None):
        super().__init__(workspaceRoot)
        self._cacheRoot = Path(cacheRoot).resolve() if cacheRoot else self._workspaceRoot.joinpath(".ccls-cache")

    async def startLspClient(self):
        super().startLspClient()
        self._lspClient = CclsLspClient(self._lspServerProc.stdout, self._lspServerProc.stdin)
        self._callGraphBuilder = CclsCallGraphBuilder(self._lspClient)
        self._callGraphManager = CallGraphManager(self._callGraphBuilder, self._callGraph)
        self._lspClient.start()
        _logger.debug(await self._lspClient.server.initialize(
            rootFolder=self._workspaceRoot,
            initializationOptions={"cacheDirectory": self._cacheRoot,
                                   "diagnostics": {"onParse": False, "onType": False},
                                   "discoverSystemIncludes": True,
                                   "enableCacheRead": True,
                                   "enableCacheWrite": True,
                                   "clang": {
                                       "excludeArgs": [],
                                       "extraArgs": ["-nocudalib"],
                                       "pathMappings": [],
                                       "resourceDir": ""
                                   }
                                   }))
        self._lspClient.server.initialized()
