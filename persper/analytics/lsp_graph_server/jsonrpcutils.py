import json
from datetime import datetime

from jsonrpc.streams import JsonRpcStreamReader, JsonRpcStreamWriter


class JsonRpcLogger():
    def __init__(self, fileName):
        self._fileName = fileName
        self._file = open(fileName, "wt")

    def logTX(self, message: dict):
        self._file.write("{0} < {1}\n".format(datetime.now(), json.dumps(message)))

    def logRX(self, message: dict):
        self._file.write("{0} > {1}\n".format(datetime.now(), json.dumps(message)))

    def __exit__(self, exc_type, exc_value, traceback):
        self._file.close()


class LoggedJsonRpcStreamReader(JsonRpcStreamReader):
    def __init__(self, rfile, logger: JsonRpcLogger):
        super().__init__(rfile)
        self._logger = logger

    def listen(self, message_consumer):
        def wrapper(message):
            self._logger.logRX(message)
            message_consumer(message)
        super().listen(wrapper)


class LoggedJsonRpcStreamWriter(JsonRpcStreamWriter):
    def __init__(self, wfile, logger: JsonRpcLogger, **json_dumps_args):
        super().__init__(wfile, **json_dumps_args)
        self._logger = logger

    def write(self, message):
        self._logger.logTX(message)
        super().write(message)
