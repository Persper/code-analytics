#!/usr/bin/env python
# -*- coding: utf-8 -*-

import os
import subprocess
import sys

from sh import git
from sh import awk

def usage(cmd):
    print("Usage: {0} [URL]".format(cmd))
    print("\tClone a git repo and show its stats.")
    print("\tIf URL is omitted, show stats of all repos in the current dir.")

def clone(repo_url):
    try:
        for line in git.clone(repo_url, _err_to_out=True, _iter=True):
            sys.stdout.write(line)
    except:
        pass

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
    if len(sys.argv) == 1:
        dirs = [d for d in os.listdir(os.getcwd()) if os.path.isdir(d) ]
        for repo_dir in dirs:
            stats(repo_dir)
    elif len(sys.argv) == 2:
        repo_url = sys.argv[1]
        repo_dir = os.path.splitext(os.path.basename(repo_url))[0]
        if os.path.isdir(repo_dir):
            print(repo_dir + " already exists.")
        else:
            clone(repo_url)
        stats(repo_dir)
    else:
        usage(sys.argv[0])

if __name__ == "__main__":
    main()

