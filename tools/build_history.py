#!/usr/bin/env python
# -*- coding: utf-8 -*-

import os
import sys
import pickle
import subprocess
from git import Repo
from persper.graphs.analyzer import Analyzer
from persper.graphs.c import CGraph
from persper.util.path import root_path


def usage(cmd):
    print("Usage: {0} [i]".format(cmd))
    print("\tBuild history for data/branch_commits_chunk[i].pickle")


def run(i):
    repo_path = os.path.join(root_path, 'repos/linux-complete')
    pickle_path = os.path.join(
        root_path, 'data/branch_commits_chunk' + i + '.pickle')
    with open(pickle_path, 'rb') as f:
        sha_lst = pickle.load(f)

    az = Analyzer(repo_path, CGraph())
    r = Repo(repo_path)
    chunk_commits = [r.commit(sha) for sha in sha_lst]
    az.build_history(chunk_commits, phase='history-chunk-' + i)


def main():
    if len(sys.argv) == 2:
        i = sys.argv[1]
        run(i)
    else:
        usage(sys.argv[0])

if __name__ == "__main__":
    main()
