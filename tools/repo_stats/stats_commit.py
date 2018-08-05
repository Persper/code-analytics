#!/usr/bin/env python3

import argparse
import git
import json
import re
import sys


def main():
    parser = argparse.ArgumentParser(
        description='List commit stats of a git repo')
    parser.add_argument('-d', '--repo-dir', required=True,
                        help='Dir of the repo to analyze')
    parser.add_argument('-b', '--branch', default='master',
                        help='Branch of the repo to analyze')
    parser.add_argument('-f', '--output-file',
                        help='Output JSON file')
    parser.add_argument('-s', '--show-stats', action='store_true',
                        help='Show aggregated stats of authors instead of outputting commits to a JSON file')
    parser.add_argument('-l', '--min-count', type=int, default=0,
                        help='Min number of commit to begin with')
    parser.add_argument('-u', '--max-count', type=int, default=sys.maxsize,
                        help='Max number of commit to end with')
    args = parser.parse_args()

    repo = git.Repo(args.repo_dir)
    commits = repo.iter_commits(args.branch, max_count=args.max_count,
                                skip=args.min_count)
    if args.show_stats:
        email2stats = {}
        for i, commit in enumerate(commits):
            if len(commit.parents) > 1:
                continue
            email = commit.author.email.lower()
            if email not in email2stats:
                email2stats[email] = {'commits': 1, 'begin': i, 'end': i,
                                      'names': [commit.author.name]}
            else:
                stats = email2stats[email]
                stats['commits'] += 1
                stats['end'] = i
                if commit.author.name not in stats['names']:
                    stats['names'].append(commit.author.name)

        print('#\tEmail\tCommit count\tBegin index\tEnd index\tAuthor names')
        sorted_items = sorted(email2stats.items(), key=lambda x: x[1]['commits'], reverse=True)
        for i, item in enumerate(sorted_items, start=1):
            email, stats = item
            print('%d\t%s\t%d\t%d\t%d\t' % (i, email, stats['commits'], stats['begin'], stats['end']), stats['names'])
        return

    if not args.output_file:
        sys.exit('Error: Specify either --show-stats or --output-file. '
                 'See more info with -h.')

    outfile = open(args.output_file, 'w')
    commit_list = []

    user_name, repo_name = re.split('[/:.]', repo.remotes.origin.url)[-3:-1]
    url_base = 'https://github.com/%s/%s/commit/' % (user_name, repo_name)

    for commit in commits:
        if len(commit.parents) > 1:
            continue
        n_add = 0
        n_del = 0
        files = []
        for path, stat in commit.stats.files.items():
            files.append(path)
            n_add += stat['insertions']
            n_del += stat['deletions']

        commit_list.append({
              'hash': commit.hexsha,
              'url': url_base + commit.hexsha,
              'email': commit.author.email.lower(),
              'summary': commit.summary,
              'additions': n_add,
              'deletions': n_del,
              'files': len(files),
              'file_list': files})

    json.dump(commit_list, outfile)
    outfile.close()


if __name__ == '__main__':
    main()
