#!/usr/bin/env python
# -*- coding: utf-8 -*-

import argparse
import os
import re
from sets import Set
from sh.contrib import git
import sys
import threading

import github_comments
import jira_issue

_jira_issue = jira_issue.JiraIssue()
_github_comments = github_comments.GitHubComments()

def process_log(log, key, repo, dir_path):
    commit = re.match("(commit )(\w{10})", log).group(2)
    file_prefix = commit + "-"

    m = re.findall(key + "-\d+", log)
    ids = Set(m)
    for i in ids:
        file_name = file_prefix + i + ".xml"
        _jira_issue.download(i, dir_path, file_name)
    
    m = re.findall("(?:[Cc]lose[ds]*|[Pp]ull[ \t]*[Rr]equest|[Mm]erge[ds]*)" \
                   "[ \t]*#\d+",
                   log)
    prs = Set(m)
    for pr in prs:
        pr = pr.split("#")[1]
        file_path = os.path.join(dir_path,
                                 file_prefix + "GitHub-" + pr + ".xml")
        invalid_path = os.path.join(dir_path,
                   ".invalid." + file_prefix + "GitHub-" + pr + ".xml")
        if os.path.isfile(file_path) or os.path.isfile(invalid_path):
            continue
        print "Downloading for", commit, "from GitHub:", repo, pr
        _github_comments.download("apache", repo, pr, file_path)

def crawl_repo(repo_dir, key, tag, n):
    # Prepare the dir to store issues.
    repo = os.path.basename(repo_dir)
    path = repo + "-issues"
    if not os.path.isdir(path):
        os.mkdir(path)
    git_repo = git.bake("-C", os.path.expanduser(repo_dir))
    git_repo.checkout(tag)
    for i in range(int(n)):
        try:
            log_str = str(git_repo.log("-1", "HEAD~" + str(i)))
        except Exception as e:
            print repo_dir, "ends at", i, "commits"
            break
        process_log(log_str, key, repo, path)

def main():
    parser = argparse.ArgumentParser()
    parser.add_argument("-f", "--config-file",
                        help= "config file path",
                        type=str, required=True)
    github_comments.add_args(parser)
    args = parser.parse_args()

    _github_comments.login(args.github_user, args.github_password)

    conf_file = open(args.config_file)
    threads = []
    for line in conf_file:
        if line.startswith("#"):
            continue
        repo_args = tuple(line.split())
        t = threading.Thread(target=crawl_repo, args=line.split())
        threads.append(t)
        t.start()

    for t in threads:
        t.join()

if __name__ == "__main__":
    main()
