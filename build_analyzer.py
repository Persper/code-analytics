import os
import pytest
import pickle
import subprocess
from persper.analytics.cpp import CPPGraphServer
from persper.analytics.analyzer import Analyzer
from persper.analytics.iterator import RepoIterator
from persper.util.path import root_path
from persper.analytics.graph_server import CPP_FILENAME_REGEXES
import argparse
import shutil
import glob
import subprocess
import tempfile
from lxml import etree

ALPHA = 0.85

def build_analyzer(pickle_path, repo_path):
	print('LOL')
	az = Analyzer(repo_path, CPPGraphServer(CPP_FILENAME_REGEXES))
	az.analyze(pickle_path, from_beginning=True, into_branches=True)
	return pickle_path

# if __name__ == '__main__':
#     parser = argparse.ArgumentParser()
#     parser.add_argument('REPO_PATH', help='source dir', type=str)
#     args = parser.parse_args()
#     build_analyzer(args.REPO_PATH)