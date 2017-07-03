#!/usr/bin/env python2
# -*- coding: utf-8 -*-

import argparse
from sh.contrib import git
import os
import re
from sets import Set
import sys
import threading

import github_comments
import jira_issue

_jira_issue = jira_issue.JiraIssue()
_github_comments = github_comments.GitHubComments()

def process_log(log_message, key, repo_name, url, output_path, jira_only):
    log_message = str(log_message)
    commit = re.match("commit (\w{10})", log_message).group(1)
    file_prefix = commit + "-"

    if not key.lower().startswith("xxx"):
        m = re.findall(key + "-\d+", log_message)
        ids = Set(m)
        for i in ids:
            file_name = file_prefix + i + ".xml"
            _jira_issue.download(i, output_path, file_name)

    if jira_only: return

    m = re.findall("(?:[Cc]lose[ds]*|[Pp]ull\s*[Rr]equest|[Mm]erge[ds]*)" \
                   "\s*#\d+",
                   log_message)
    prs = Set(m)
    repo_user = re.search("github.com/(.*)/", url).group(1)
    for pr in prs:
        pr = pr.split("#")[-1]
        file_path = os.path.join(output_path,
                                 file_prefix + "GitHub-" + pr + ".xml")
        invalid_path = os.path.join(output_path,
                   ".invalid." + file_prefix + "GitHub-" + pr + ".xml")
        if os.path.isfile(file_path) or os.path.isfile(invalid_path):
            continue
        print "Downloading for", commit, "from GitHub:", repo_name, pr
        _github_comments.download(repo_user, repo_name, pr, file_path)

def crawl_repo(repo_dir, key, tag, url, output_dir, jira_only):
    # Prepare the repo dir.
    repo_dir = os.path.normpath(repo_dir)
    git_repo = git.bake("-C", os.path.expanduser(repo_dir))
    git_repo.fetch()
    git_repo.checkout(tag)

    # Prepare the dir to store issues.
    repo = os.path.basename(repo_dir)
    path = os.path.join(output_dir, repo + "-issues")
    if not os.path.isdir(path):
        os.makedirs(path)

    for log_line in git_repo.log('--oneline'):
        commit_id = log_line.split()[0]
        log_message = git_repo.log("-1", commit_id)
        process_log(log_message, key, repo, url, path, jira_only)

def main():
    parser = argparse.ArgumentParser()
    parser.add_argument("-f", "--config-file", required=True,
                        help="config file path")
    parser.add_argument("-o", "--output-dir", required=True,
                        help="dir for downloads")
    parser.add_argument("-j", "--jira-only", action="store_true",
                        help="only download JIRA issues")

    jira_only = "-j" in sys.argv or "--jira-only" in sys.argv
    if not jira_only:
        github_comments.add_args(parser)

    args = parser.parse_args()

    if not jira_only:
        _github_comments.login(args.github_user, args.github_password)

    conf_file = open(args.config_file)
    threads = []
    for line in conf_file:
        if line.startswith("#"):
            continue
        t = threading.Thread(target=crawl_repo,
                             args=line.split() + [ args.output_dir, jira_only ])
        threads.append(t)
        t.start()

    for t in threads:
        t.join()

if __name__ == "__main__":
    main()
