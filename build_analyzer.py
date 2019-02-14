from persper.analytics.cpp import CPPGraphServer
from persper.analytics.analyzer import Analyzer
from persper.analytics.graph_server import CPP_FILENAME_REGEXES

ALPHA = 0.85


def build_analyzer(repo_url, pickle_path, repo_path):
    az = Analyzer(repo_path, CPPGraphServer(CPP_FILENAME_REGEXES))
    az.analyze(repo_url, pickle_path, from_beginning=True, into_branches=True)
    return pickle_path
