#!/usr/bin/env python3

import argparse
import git
import json
import re

def main():
    parser = argparse.ArgumentParser(
        description='List commit stats of a git repo')
    parser.add_argument('-d', '--repo-dir', required=True,
                        help='Dir of the repo to analyze')
    parser.add_argument('-b', '--branch', default='master',
                        help='Branch of the repo to analyze')
    parser.add_argument('-o', '--output-file', required=True,
                        help='Output JSON file')
    args = parser.parse_args()

    repo = git.Repo(args.repo_dir)
    outfile = open(args.output_file, 'w')

    commit_list = []

    user_name, repo_name = re.split('[/:.]', repo.remotes.origin.url)[-3:-1]
    url_base = 'https://github.com/%s/%s/commit/' % (user_name, repo_name)

    for commit in repo.iter_commits(args.branch):
        if len(commit.parents) > 1: continue
        n_add = 0
        n_del = 0
        files = [ ]
        for path, stat in commit.stats.files.items():
            files.append(path)
            n_add += stat['insertions']
            n_del += stat['deletions']

        commit_list.append({
              'hash': commit.hexsha,
              'url': url_base + commit.hexsha,
              'email': commit.author.email,
              'summary': commit.summary,
              'additions': n_add,
              'deletions': n_del,
              'files': len(files),
              'file_list': files})

    json.dump(commit_list, outfile)
    outfile.close()

if __name__ == '__main__':
    main()
