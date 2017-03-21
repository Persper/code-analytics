#!/usr/bin/env python
# -*- coding: utf-8 -*-

import os
import re
from sets import Set
from sh.contrib import git
import sys
import threading

import jira_issue

_jira_issue = jira_issue.JiraIssue()

def process_log(log, key, dir_path):
    commit = re.match("(commit )(\w{10})", log).group(2)
    file_prefix = dir_path + "/" + commit + "-"
    m = re.findall(key + "-\d+", log)
    ids = Set(m)
    for i in ids:
        file_path = file_prefix + i + ".xml"
        if not os.path.isfile(file_path):
            _jira_issue.download(i, file_path)

def crawl_repo(repo_dir, key, tag, n):
    # Prepare the dir to store issues.
    path = os.path.basename(repo_dir) + "-issues"
    if not os.path.isdir(path):
        os.mkdir(path)

    git_repo = git.bake("-C", repo_dir)
    git_repo.checkout(tag)
    for i in range(int(n)):
        try:
            log_str = str(git_repo.log("-1", "HEAD~" + str(i)))
        except Exception as e:
            continue
        process_log(log_str, key, path)

def usage(cmd):
    print("Usage: {0} CONFIG_FILE".format(cmd))
    print("Config file format:")
    print("dir_path\tkey_word\ttag\tnum_commits")

def main():
    if len(sys.argv) != 2 or not os.path.isfile(sys.argv[1]):
        usage(sys.argv[0])
        sys.exit(1)

    conf_file = open(sys.argv[1])
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
