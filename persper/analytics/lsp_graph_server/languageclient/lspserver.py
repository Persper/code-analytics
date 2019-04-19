"""
LSP server contracts.
"""
import asyncio
import os
from collections.abc import Iterable
from pathlib import Path
from typing import Iterable, List, Tuple, Union

from jsonrpc.endpoint import Endpoint

from .lspcontract import (DocumentSymbol, FileEvent, Location, Position,
                          SymbolInformation, TextDocument,
                          TextDocumentContentChangeEvent,
                          TextDocumentSaveReason)

DEFAULT_CAPABILITIES = {
    "workspace": {
        "applyEdit": False,
        "workspaceEdit": {
            "documentChanges": True
        },
        "didChangeConfiguration": {
            "dynamicRegistration": True
        },
        "didChangeWatchedFiles": {
            "dynamicRegistration": True
        },
        "symbol": {
            "dynamicRegistration": True,
            "symbolKind": {
                "valueSet": [1, 2, 3, 4, 5, 6, 7, 8, 9, 10, 11, 12, 13, 14, 15, 16, 17, 18, 19, 20, 21, 22, 23, 24, 25, 26]
            }
        },
        "executeCommand": {
            "dynamicRegistration": True
        },
        "configuration": True,
        "workspaceFolders": False
    },
    "textDocument": {
        # ccls requires we use an object here, though LSP allows null.
        "publishDiagnostics": {},
        "synchronization": {
            "dynamicRegistration": True,
            "willSave": True,
            "willSaveWaitUntil": True,
            "didSave": True
        },
        "completion": {
            "dynamicRegistration": True,
            "contextSupport": True,
            "completionItem": {
                "snippetSupport": True,
                "commitCharactersSupport": True,
                "documentationFormat": ["markdown", "plaintext"]
            },
            "completionItemKind": {
                "valueSet": [1, 2, 3, 4, 5, 6, 7, 8, 9, 10, 11, 12, 13, 14, 15, 16, 17, 18, 19, 20, 21, 22, 23, 24, 25]
            }
        },
        "hover": {
            "dynamicRegistration": True,
            "contentFormat": ["markdown", "plaintext"]
        },
        "signatureHelp": {
            "dynamicRegistration": True,
            "signatureInformation": {
                "documentationFormat": ["markdown", "plaintext"]
            }
        },
        "definition": {
            "dynamicRegistration": True
        },
        "references": {
            "dynamicRegistration": True
        },
        "documentHighlight": {
            "dynamicRegistration": True
        },
        "documentSymbol": {
            "dynamicRegistration": True,
            "symbolKind": {
                "valueSet": [1, 2, 3, 4, 5, 6, 7, 8, 9, 10, 11, 12, 13, 14, 15, 16, 17, 18, 19, 20, 21, 22, 23, 24, 25, 26]
            },
            "hierarchicalDocumentSymbolSupport": True
        },
        "codeAction": {
            "dynamicRegistration": True
        },
        "codeLens": {
            "dynamicRegistration": True
        },
        "formatting": {
            "dynamicRegistration": True
        },
        "rangeFormatting": {
            "dynamicRegistration": True
        },
        "onTypeFormatting": {
            "dynamicRegistration": True
        },
        "rename": {
            "dynamicRegistration": True
        },
        "documentLink": {
            "dynamicRegistration": True
        },
        "typeDefinition": {
            "dynamicRegistration": True
        },
        "implementation": {
            "dynamicRegistration": True
        },
        "colorProvider": {
            "dynamicRegistration": True
        }
    }}


class LspServerStub():
    def __init__(self, endpoint: Endpoint):
        if not isinstance(endpoint, Endpoint):
            raise TypeError("Expect Endpoint instance.")
        self._endpoint = endpoint

    def request(self, method, params=None):
        return asyncio.wrap_future(self._endpoint.request(method, params))

    def notify(self, method, params=None):
        self._endpoint.notify(method, params)

    def initialize(self, processId=None, rootFolder=None, initializationOptions=None, capabilities=None):
        if processId is None:
            processId = os.getpid()
        cap = DEFAULT_CAPABILITIES.copy()
        if capabilities:
            cap.update(capabilities)
        rootUri = Path(rootFolder).as_uri()
        return self.request("initialize", {
            "processId": processId,
            "rootUri": rootUri,
            "initializationOptions": initializationOptions,
            "capabilities": cap
        })

    def initialized(self):
        self.notify("initialized")

    def shutdown(self):
        return self.request("shutdown")

    def exit(self):
        self.notify("exit")

    def textDocumentDidOpen(self, document: TextDocument):
        self.notify("textDocument/didOpen", {"textDocument": document.toDict()})

    def textDocumentDidClose(self, documentUri: str):
        self.notify("textDocument/didClose", {"textDocument": {"uri": documentUri}})

    async def textDocumentGotoDefinition(self, documentUri: str, position: Union[Tuple[int, int], Position],
                                         requestParamsOverride: dict = None):
        requestParams = {
            "textDocument": {"uri": documentUri},
            "position": Position.parse(position).toDict()
        }
        if requestParamsOverride:
            requestParams.update(requestParamsOverride)
        result = await self.request("textDocument/definition", requestParams)
        if not result:
            return []
        if isinstance(result, Iterable):
            return [Location.fromDict(r) for r in result]
        return [Location.fromDict(result)]

    async def textDocumentGetSymbols(self, documentUri: str, requestParamsOverride: dict = None) -> List[DocumentSymbol]:
        requestParams = {"textDocument": {"uri": documentUri}}
        if requestParamsOverride:
            requestParams.update(requestParamsOverride)
        result = await self.request("textDocument/documentSymbol", requestParams)
        if not result:
            return []

        def fromDict(d: dict):
            if "location" in d:
                return SymbolInformation.fromDict(d)
            return DocumentSymbol.fromDict(d)

        return [fromDict(d) for d in result]

    def textDocumentDidChange(self, documentUri: str, documentVersion: int, contentChanges: Iterable[TextDocumentContentChangeEvent]):
        self.notify("textDocument/didChange", {"textDocument": {"uri": documentUri, "version": documentVersion},
                                               "contentChanges": [c.toDict() for c in contentChanges]})

    def textDocumentWillSave(self, documentUri: str, reason: TextDocumentSaveReason = TextDocumentSaveReason.Manual):
        self.notify("textDocument/willSave", {"textDocument": {"uri": documentUri},
                                              "reason": reason.value})

    def textDocumentDidSave(self, documentUri: str, text: str = None):
        self.notify("textDocument/didSave", {"textDocument": {"uri": documentUri},
                                             "text": text})

    async def textDocumentCodeLens(self, documentUri: str):
        result = await self.request("textDocument/codeLens", {"textDocument": {"uri": documentUri}})
        # We call this method only to synchronize the time sequence
        return result

    def workspaceDidChangeWatchedFiles(self, changes: Iterable[FileEvent]):
        self.notify("workspace/didChangeWatchedFiles", {"changes": [c.toDict() for c in changes]})
