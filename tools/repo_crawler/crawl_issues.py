#!/usr/bin/env python2
# -*- coding: utf-8 -*-

import argparse
from sh.contrib import git
import os
import re
from sets import Set
import sys
import threading
import traceback

import github_comments
import jira_issue

_jira_issue = jira_issue.JiraIssue()
_github_comments = github_comments.GitHubComments()

def process_log(log_message, key, repo_name, url, output_path, jira_only):
    try:
        log_message = str(log_message)
    except Exception as e:
        print "[Error] process_log: ", type(e)
        print >> sys.stderr, repo_name + ": ", e
        traceback.print_exc()
        return
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
    repo_dir = os.path.expanduser(repo_dir)
    if not os.path.isdir(repo_dir):
        try:
            git.clone(url, repo_dir)
        except Exception as e:
            print "[Error] crawl_repo: clone: ", type(e)
            print >> sys.stderr, repo_dir
            print >> sys.stderr, e
            return
    git_repo = git.bake("-C", repo_dir)
    try:
        git_repo.fetch()
    except Exception as e:
        print "[Error] crawl_repo: fetch ", type(e)
        print >> sys.stderr, e
    try:
        git_repo.checkout(tag)
    except Exception as e:
        print "[Error] crawl_repo: checkout ", type(e)
        print >> sys.stderr, e

    # Prepare the dir to store issues.
    repo = os.path.basename(repo_dir)
    path = os.path.join(output_dir, repo + "-issues")
    if not os.path.isdir(path):
        os.makedirs(path)

    for log_line in git_repo.log("--oneline"):
        commit_id = log_line.split()[0]
        log_message = git_repo.log("-1", commit_id)
        process_log(log_message, key, repo, url, path, jira_only)

def crawler_thread(index, num_threads, lines, output_dir, jira_only):
    for i, line in enumerate(lines):
        if line.startswith("#"):
            continue
        if i % num_threads == index:
            repo_dir, key, tag, url = line.split()
            try:
                crawl_repo(repo_dir, key, tag, url, output_dir, jira_only)
            except Exception as e:
                print >> sys.stderr, repo_dir, e
                traceback.print_exc()

def main():
    parser = argparse.ArgumentParser()
    parser.add_argument("-f", "--config-file", required=True,
                        help="config file path")
    parser.add_argument("-o", "--output-dir", required=True,
                        help="dir for downloads")
    parser.add_argument("-j", "--jira-only", action="store_true",
                        help="only download JIRA issues")
    parser.add_argument("-t", "--num-threads", type=int, default=4,
                        help="number of downloading threads")
    jira_only = "-j" in sys.argv or "--jira-only" in sys.argv
    if not jira_only:
        github_comments.add_args(parser)

    args = parser.parse_args()

    if not jira_only:
        _github_comments.login(args.github_user, args.github_password)

    conf_file = open(args.config_file)
    threads = []
    lines = conf_file.readlines()
    for index in range(args.num_threads):
        t = threading.Thread(target=crawler_thread,
            args=(index, args.num_threads, lines, args.output_dir, jira_only))
        t.daemon = True
        threads.append(t)
        t.start()

    for t in threads:
        t.join()

    conf_file.close()

if __name__ == "__main__":
    main()
