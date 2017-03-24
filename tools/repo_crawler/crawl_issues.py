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
    file_prefix = dir_path + "/" + commit + "-"

    m = re.findall(key + "-\d+", log)
    ids = Set(m)
    for i in ids:
        file_path = file_prefix + i + ".xml"
        if not os.path.isfile(file_path):
            _jira_issue.download(i, file_path)
    
    m = re.findall("Closes #\d+", log)
    prs = Set(m)
    for pr in prs:
        pr = pr[8:]
        file_path = file_prefix + "GitHub-" + pr + ".xml"
        if not os.path.isfile(file_path):
            print "Downloading for", commit, "from GitHub:", repo, pr
            _github_comments.download("apache", repo, pr, file_path)

def crawl_repo(repo_dir, key, tag, n):
    # Prepare the dir to store issues.
    repo = os.path.basename(repo_dir)
    path = repo + "-issues"
    if not os.path.isdir(path):
        os.mkdir(path)

    git_repo = git.bake("-C", repo_dir)
    git_repo.checkout(tag)
    for i in range(int(n)):
        try:
            log_str = str(git_repo.log("-1", "HEAD~" + str(i)))
        except Exception as e:
            continue
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
        repo_args = tuple(line.split())
        t = threading.Thread(target=crawl_repo, args=line.split())
        threads.append(t)
        t.start()

    for t in threads:
        t.join()

if __name__ == "__main__":
    main()
