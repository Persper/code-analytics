from persper.analytics.analyzer2 import Analyzer
from persper.analytics.c import CGraphServer
from persper.analytics.cpp import CPPGraphServer
from persper.analytics.graph_server import C_FILENAME_REGEXES
from persper.analytics.graph_server import CPP_FILENAME_REGEXES


def supported_analyzer(repo_path, language):
    supported_analyzers = {
        'C': Analyzer(repo_path, CGraphServer(C_FILENAME_REGEXES), firstParentOnly=True),
        'C++': Analyzer(repo_path, CPPGraphServer(CPP_FILENAME_REGEXES), firstParentOnly=True)
    }

    return supported_analyzers[language]
