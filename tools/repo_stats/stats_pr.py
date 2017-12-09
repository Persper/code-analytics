#!/usr/bin/env python3
# -*- coding: utf-8 -*-

import argparse
import os
import re
import sys

from sh.contrib import git
from sh import wc


def jira_issue(commit_message, key):
    if key is None:
        return []
    matches = re.findall(key + "-\d+(?!\d*.\d+)", commit_message, re.IGNORECASE)
    return [m.upper() for m in matches]


def parse_pr(commit_message):
    matches = re.findall("(?:close[ds]*|"
                         "pull\s*request|"
                         "fix(?:e[ds])?|"
                         "merge[ds]*)"
                         "\s*#\d+",
                         commit_message, re.IGNORECASE)
    return [m.split('#')[-1] for m in matches]


def num_commits(repo_dir):
    git_repo = git.bake('-C', os.path.expanduser(repo_dir))
    logs = git_repo.log('--oneline', '--first-parent')
    n = wc(logs, '-l')
    return int(n)


def stats_pr(repo_dir, key, begin, end):
    """Lists the number of PR/issue-based commits in the range
    """
    git_repo = git.bake('-C', os.path.expanduser(repo_dir))
    num = 0
    prs = []
    for i in range(begin, end):
        message = str(git_repo.log('--first-parent', '-1', 'HEAD~' + str(i)))
        pi = []
        pi += jira_issue(message, key)
        pi += parse_pr(message)
        if pi:
            num += 1
            prs += pi
    return num, prs


def main():
    parser = argparse.ArgumentParser(
        description='Stats commits through pull requests/issues')
    parser.add_argument('-n', '--num-groups', type=int, required=True,
                        help='number of groups of commits in stats')
    parser.add_argument('-d', '--dir', required=True,
                        help='dir of the git repo')
    parser.add_argument('-k', '--key', help='key of JIRA issue')
    parser.add_argument('-t', '--tag', help='tag to check out of the repo')
    parser.add_argument('-m', '--max', type=int,
                        help='max number of commits to process')
    args = parser.parse_args()

    if not os.path.isdir(args.dir):
        sys.exit('Error: ' + args.dir + ' is not a valid dir!')

    if args.tag:
        git_repo = git.bake('-C', os.path.expanduser(args.dir))
        git_repo.checkout(args.tag)

    print(os.path.basename(os.path.normpath(args.dir)))
    n = num_commits(args.dir)
    if args.max < n:
        n = args.max
    n //= args.num_groups
    for i in reversed(range(args.num_groups)):
        np, prs = stats_pr(args.dir, args.key, i * n, (i + 1) * n)
        print(np / n, end=',')
        print('"{0}"'.format(','.join(prs)))


if __name__ == '__main__':
    main()
