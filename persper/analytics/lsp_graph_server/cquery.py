import logging
from asyncio import sleep
from pathlib import Path, PurePath

from antlr4 import Token
from jsonrpc.endpoint import Endpoint
from jsonrpc.exceptions import JsonRpcException

from persper.analytics.lsp_graph_server.callgraph.builder import CallGraphBuilder
from persper.analytics.lsp_graph_server.fileparsers.CPP14Lexer import CPP14Lexer
from persper.analytics.lsp_graph_server.languageclient.lspclient import LspClient
from persper.analytics.lsp_graph_server.languageclient.lspcontract import TextDocument
from persper.analytics.lsp_graph_server.languageclient.lspserver import LspServerStub

_logger = logging.getLogger(__name__)


class CQueryLspServerStub(LspServerStub):
    def __init__(self, endpoint: Endpoint):
        super().__init__(endpoint)

    def freshenIndex(self):
        self.notify("$cquery/freshenIndex")

    def textDocumentDidView(self, documentUri: str):
        self.notify("$cquery/textDocumentDidView", {"textDocumentUri": documentUri})


class CQueryLspClient(LspClient):
    def __init__(self, rx, tx):
        super().__init__(rx, tx)
        self._serverStub = CQueryLspServerStub(self._endpoint)
        self._isBusy = False

    @property
    def isBusy(self):
        return self._isBusy

    def m_cquery__progress(self, indexRequestCount=0, doIdMapCount=0, loadPreviousIndexCount=0, onIdMappedCount=0, onIndexedCount=0, activeThreads=0):
        # See https://github.com/cquery-project/vscode-cquery/blob/8ded1bd94548f9341bd9f1f1a636af01602012e0/src/extension.ts#L559
        total = indexRequestCount + doIdMapCount + loadPreviousIndexCount + onIdMappedCount + onIndexedCount + activeThreads
        self._isBusy = total > 0
        _logger.log(logging.INFO if total > 0 else logging.DEBUG, "Req:%d IdMap:%d/%d/%d Threads:%d",
                    indexRequestCount, doIdMapCount, onIdMappedCount, onIndexedCount, activeThreads)


class CQueryCallGraphBuilder(CallGraphBuilder):
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

    def __init__(self, lspClient: LspClient):
        if not isinstance(lspClient, CQueryLspClient):
            raise TypeError("lspClient should be an instance of CQueryLspClient.")
        super().__init__(CPP14Lexer, lspClient)

    def filterToken(self, token: Token):
        return token.type in self._tokensOfInterest

    def inferLanguageId(self, path: PurePath):
        return "cpp"

    def modifyFile(self, fileName: str, newContent: str):
        old = super().modifyFile(fileName, newContent)
        self._lspClient.server.freshenIndex()
        return old

    async def openDocument(self, textDoc: TextDocument):
        self._lspClient.server.textDocumentDidOpen(textDoc)
        while True:
            try:
                while self._lspClient.isBusy:
                    await sleep(1)
                await self._lspClient.server.textDocumentCodeLens(textDoc.uri)
                return
            except JsonRpcException as ex:
                # cquery specific
                if ex.code == -32603 and "Unable to find file" in ex.message:
                    _logger.warning("Language server is not ready. Waiting…")
                    await sleep(5)
