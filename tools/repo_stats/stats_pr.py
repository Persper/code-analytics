#!/usr/bin/env python3
# -*- coding: utf-8 -*-

import argparse
from sh.contrib import git
import os
import re
from sh import wc

def jira_issue(commit_message, key):
    if key is None:
        return []
    matches = re.findall(key + "-\d+(?!\d*.\d+)", commit_message, re.IGNORECASE)
    return [m.upper() for m in matches]

def parse_pr(commit_message):
    matches = re.findall("(?:close[ds]*|"
                         "pull\s*request|"
                         "fix(e[ds]){0,1}|"
                         "merge[ds]*)"
                         "\s*#\d+",
                         commit_message, re.IGNORECASE)
    return [m.split('#')[-1] for m in matches]

def num_commits(repo_dir):
    git_repo = git.bake("-C", os.path.expanduser(repo_dir))
    logs = git_repo.log('--oneline', '--first-parent')
    n = wc(logs, '-l')
    return int(n)

def stats_pr(repo_dir, key, num_groups, n):
    """Lists the number of commits through pull requests/issues every n commits
    """
    git_repo = git.bake("-C", os.path.expanduser(repo_dir))
    num_prs = []
    for g in range(num_groups):
        p = 0
        for i in range(g * n, (g + 1) * n):
            message = str(git_repo.log("-1", "HEAD~" + str(i)))
            if jira_issue(message, key) or parse_pr(message):
                p += 1
        num_prs.append(p)
    num_prs.reverse()
    return num_prs

def main():
    parser = argparse.ArgumentParser(
        description='Stats commits through pull requests/issues')
    parser.add_argument('-n', '--num-groups', type=int, required=True,
        help='number of groups of commits in stats')
    parser.add_argument('-d', '--dir', required=True,
        help='dir of the git repo')
    parser.add_argument('-k', '--key', help='key of JIRA issue')
    parser.add_argument('-m', '--max', type=int,
        help='max number of commits to process')
    args = parser.parse_args()

    if os.path.isdir(args.dir):
        n = num_commits(args.dir)
        if args.max < n:
            n = args.max
        n //= args.num_groups
        num_prs = stats_pr(args.dir, args.key, args.num_groups, n)
        print(os.path.basename(os.path.normpath(args.dir)))
        for np in num_prs:
            print(np / n)
    else:
        print('Error: ' + args.dir + ' is not a valid dir!')

if __name__ == '__main__':
    main()

