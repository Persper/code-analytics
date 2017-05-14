#!/usr/bin/env python3
# -*- coding: utf-8 -*-

import argparse
from sh import awk
from sh import git
import os
import subprocess
import sys


def stats(repo_dir):
    print(repo_dir + ":")
    print("\tTop authors [author] [# commits]")
    git_cmd = ["git", "-C", repo_dir, "shortlog", "-sn"]
    commits_per_author = subprocess.Popen(git_cmd, stdout=subprocess.PIPE)
    awk_script = '''
    BEGIN { count_commits = 0 }
    { count_commits += $1; if (NR <= 10) print "\t" $2 "\t" $1 }
    END { print "# total commits: " count_commits }
    '''
    print(awk(awk_script, _in=commits_per_author.stdout))

def main():
    parser = argparse.ArgumentParser(
        description='List author stats of git repos')
    parser.add_argument('dir', nargs='+', help='Dir of a git repo')
    args = parser.parse_args()

    for repo_dir in args.dir:
        if os.path.isdir(repo_dir):
            stats(repo_dir)
        else:
            print('Error: ' + repo_dir + ' is not a valid dir!')

if __name__ == "__main__":
    main()

