import asyncio
import logging
import subprocess
from os import path, sys

from callgraph.manager import CallGraphManager
from ccls import CclsCallGraphBuilder, CclsLspClient

# Thus you need to place cquery in rootfolder/bin/cquery, and execute ./src/main.py in root folder.
LANGUAGE_SERVER_COMMAND = "./bin/cquery --record cquerystd --log-file cquery.log --ci"  # --log-all-to-stderr"
LANGUAGE_SERVER_COMMAND = "./bin/ccls -log-file=ccls.log"
SOURCE_ROOT = "./demoroot/cpp/"
CACHE_ROOT = "./demoroot/cache/"
# SOURCE_ROOT = "./demoroot/cpp-simple/"
ENTRYPOINT_PATTERN = path.join(SOURCE_ROOT, "./Eigen/src/Cholesky/*.h")
JSON_RPC_DUMP_PATH = "rpctrace.txt"

logging.basicConfig(format='%(asctime)s %(levelname)-8s [%(name)s] %(message)s',
                    level=logging.INFO)
logging.getLogger('asyncio').setLevel(logging.CRITICAL)


async def main():
    logger = logging.getLogger()
    # an simple approach to let user change entrypoint file from commandline arguments
    global ENTRYPOINT_PATTERN, SOURCE_ROOT
    if (len(sys.argv) == 2):
        ENTRYPOINT_PATTERN = sys.argv[1]
    elif (len(sys.argv) == 3):
        SOURCE_ROOT, ENTRYPOINT_PATTERN = sys.argv[1], sys.argv[2]
    with subprocess.Popen(LANGUAGE_SERVER_COMMAND, stdin=subprocess.PIPE, stdout=subprocess.PIPE,
                          creationflags=subprocess.CREATE_NEW_CONSOLE) as serverProc:
        try:
            logger.info("Started language server with PID: %d.", serverProc.pid)
            client = CclsLspClient(serverProc.stdout, serverProc.stdin, JSON_RPC_DUMP_PATH)
            client.start()
            logger.info(await client.server.initialize(
                rootFolder=path.abspath(SOURCE_ROOT),
                initializationOptions={"cacheDirectory": path.abspath(CACHE_ROOT),
                                       "diagnostics": {"onParse": False, "onType": False},
                                       "discoverSystemIncludes": True,
                                       "enableCacheRead": True,
                                       "enableCacheWrite": True,
                                       "progressReportFrequencyMs": 500,
                                       "clang": {
                                            "excludeArgs": [],
                                            "extraArgs": ["-nocudalib"],
                                            "pathMappings": [],
                                            "resourceDir": ""
                                        }
                                        }))
            client.server.initialized()

            builder = CclsCallGraphBuilder(client)
            builder.workspaceFilePatterns = [path.abspath(path.join(SOURCE_ROOT, "/**/*"))]
            manager = CallGraphManager(builder)
            await manager.buildGraph(ENTRYPOINT_PATTERN)
            manager.graph.dumpTo("graph.txt")

            testFile = path.join(SOURCE_ROOT, "Utility.h")
            if path.exists(testFile):
                for i in range(2):
                    logger.info("Now we are replacing Utility.h with a single line of content.")
                    oldContent = builder.modifyFile(testFile, "// Removed file content.")
                    await manager.rebuildGraph([testFile])
                    manager.graph.dumpTo("graph1.txt")
                    logger.info("Now we are restoring Utility.h.")
                    builder.modifyFile(testFile, oldContent)
                    await manager.rebuildGraph([testFile])
                    manager.graph.dumpTo("graph2.txt")

            logger.info("Shutting down language server...")
            await asyncio.wait_for(client.server.shutdown(), 10)
            client.server.exit()
            logger.info("Language server exited with code: %s.", serverProc.wait(10))
        finally:
            if serverProc.returncode is None:
                # kill server process to avoid infinite wait in Popen.__exit__
                serverProc.kill()
                logger.warning("Killed language server.")


if __name__ == '__main__':
    loop = asyncio.new_event_loop()
    loop.set_debug(True)
    loop.run_until_complete(main())
