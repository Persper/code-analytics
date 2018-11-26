"""
LSP client implementation.
"""
import logging
import threading

from jsonrpc.dispatchers import MethodDispatcher
from jsonrpc.endpoint import Endpoint
from jsonrpc.streams import JsonRpcStreamReader, JsonRpcStreamWriter

from persper.analytics.lsp_graph_server.languageclient.lspcontract import MessageType
from persper.analytics.lsp_graph_server.languageclient.lspserver import LspServerStub
from persper.analytics.lsp_graph_server.jsonrpcutils import LoggedJsonRpcStreamReader, LoggedJsonRpcStreamWriter, JsonRpcLogger

_logger = logging.getLogger(__name__)


class LspClient(MethodDispatcher):
    def __init__(self, rx, tx, logFile: str = None):
        super().__init__()
        self._rpclogger = JsonRpcLogger(logFile) if logFile else None
        self._streamReader = LoggedJsonRpcStreamReader(rx, self._rpclogger) if logFile else JsonRpcStreamReader(rx)
        self._streamWriter = LoggedJsonRpcStreamWriter(tx, self._rpclogger) if logFile else JsonRpcStreamWriter(tx)
        self._nextJsonRpcMessageId = 0
        # Some language server, e.g. cquery, only supports numerical request Ids.
        self._endpoint = Endpoint(self, self._streamWriter.write, self.nextJsonRpcMessageId)
        self._listenerThread = None
        self._shutdownEvent = threading.Event()
        self._serverStub = LspServerStub(self._endpoint)

    def nextJsonRpcMessageId(self):
        self._nextJsonRpcMessageId += 1
        if self._nextJsonRpcMessageId >= 0x7FFFFFFF:
            self._nextJsonRpcMessageId = 0
        return str(self._nextJsonRpcMessageId)

    def start(self):
        self._listenerThread = threading.Thread(target=self._startListener, daemon=True)
        self._listenerThread.start()

    def stop(self):
        self._endpoint.shutdown()
        self._streamReader.close()
        self._streamWriter.close()
        self._shutdownEvent.set()
        self._listenerThread.join(timeout=30)

    def initializeServer(self):
        raise NotImplementedError()

    @property
    def server(self):
        return self._serverStub

    def _startListener(self):
        self._streamReader.listen(self._endpoint.consume)

    def m_window__show_message(self, type: MessageType, message: str):
        type = MessageType(type)
        _logger.info(type, message)

    def m_window__show_message_request(self, type: MessageType, message: str, actions):
        type = MessageType(type)
        print(type, message, actions)
        return actions[0]["title"]

    def m_window__log_message(self, type: MessageType, message: str):
        type = MessageType(type)
        _logger.info(type, message)

    def m_text_document__publish_diagnostics(self, uri: str, diagnostics):
        # ignore all diagnostic information for now.
        pass
