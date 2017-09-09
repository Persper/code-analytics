#!/usr/bin/env python3
# -*- coding: utf-8 -*-

import argparse
from sh.contrib import git
import os
import subprocess
import sys

def stats_commits(repo_path, author_stats=None):
    if not author_stats:
        author_stats = { }
    git_cmd = ['git', '--no-pager', '-C', repo_path, 'shortlog', '-sn']
    p = subprocess.Popen(git_cmd, stdout=subprocess.PIPE)
    with os.fdopen(os.dup(p.stdout.fileno())) as commits_per_author:
        for line in commits_per_author:
            num, name = [s.strip() for s in line.split('\t')]
            if not name in author_stats:
                author_stats[name] = { 'n_commits': int(num) }
            else:
                author_stats[name]['n_commits'] = int(num)
    return author_stats

def main():
    parser = argparse.ArgumentParser(
        description='List author stats of git repo(s)')
    parser.add_argument('-c', '--count-commits', metavar='DIR',
                        help='Git repo dir to list authors and their # commits')
    parser.add_argument('-a', '--count-authors', metavar='DIR', nargs='+',
                        help='Multiple git repos to list their # authors')
    args = parser.parse_args()
    if args.count_commits:
        if not os.path.isdir(args.count_commits):
            sys.exit('Error: ' + args.dir + ' is not a valid dir!')
        author_stats = stats_commits(args.count_commits)
        for name, stats in sorted(author_stats.items(),
                                  key=lambda x: x[1]['n_commits'],
                                  reverse=True):
            print(name, stats['n_commits'], sep=',')
    elif args.count_authors:
        project_authors = { }
        for d in args.count_authors:
            if os.path.isfile(d) or d.startswith('.'):
                continue
            repo_name = os.path.basename(os.path.normpath(d))
            print('Parsing ' + repo_name)
            project_authors[repo_name] = stats_commits(d)
        for repo_name, author_stats in sorted(project_authors.items(),
                                            key=lambda x: len(x[1]),
                                            reverse=True):
            print(repo_name, len(author_stats), sep=',')
    else:
        sys.exit('Error: see -h for usage.')

if __name__ == '__main__':
    main()

