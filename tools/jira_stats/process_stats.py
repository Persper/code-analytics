#!/usr/bin/env python3

import argparse
import os
import re

def find_github(name, urls):
    candidates = [ ]
    target = set(x.lower() for x in name.split() if len(x) > 1)
    for item in urls:
        name_set = set(x.lower() for x in item['name'].split() if len(x) > 1)
        if target <= name_set:
            candidates.append({
                'name': item['name'],
                'github_repo': item['github_repo']
            })
    return candidates

def main():
    parser = argparse.ArgumentParser(
        description='Select projects to produce the config file for'
                    'the JIRA issue crawler')
    parser.add_argument('-s', '--stats-file', required=True,
                        help='the project issue stats file '
                             'produced by global_stats')
    parser.add_argument('-u', '--url-file', required=True,
                        help='the git url file produced by collect_git_urls')
    parser.add_argument('-d', '--parent-dir', required=True,
                        help='the dir to contain repos')
    parser.add_argument('-o', '--output-file', required=True,
                        help='output file')
    args = parser.parse_args()

    issue_stats = [ ]
    with open(args.stats_file, 'r') as stats:
        for line in stats:
            name, key, id, count, \
                feature, bug, improvement, maintenance, \
                high, mid, low = line.split(',')
            if name == 'name' and key == 'key': continue
            issue_stats.append({
                'name': name, 'key': key, 'id': id, 'count': count,
                'feature': feature, 'bug': bug,
                'improvement': improvement, 'maintenance': maintenance,
                'high': high, 'mid': mid, 'low': low
            })

    project_urls = [ ] 
    with open(args.url_file, 'r') as urls:
        for line in urls:
            name, apache_repo, github_repo = line.split(',')
            project_urls.append({
                'name': name,
                'apache_repo': apache_repo,
                'github_repo': github_repo
            })

    out_file = open(args.output_file, 'w')
    empty_file = open(args.output_file + '.empty', 'w')

    re_name = re.compile(r'https\://github\.com/apache/(\S+)')
    for project in issue_stats:
        candidates = find_github(project['name'], project_urls)
        if len(candidates) == 0:
            print(args.parent_dir, project['key'], 'master',
                  sep='\t', file=empty_file)
            continue
        for candidate in candidates:
            github = candidate['github_repo'].strip()
            dir_name = re_name.search(github).group(1)
            path = os.path.join(args.parent_dir, dir_name)
            print(path, project['key'], 'master', github + '.git',
                  sep='\t', file=out_file)

    empty_file.close()
    out_file.close()

if __name__ == '__main__':
    main()

