#!/usr/bin/env python3

import argparse
import os
import re
import requests
import sys


def main():
    parser = argparse.ArgumentParser(
        description='Collect Apache and GitHub repo URLs of Apache projects')
    parser.add_argument('-f', '--file', required=True,
                        help='the output file')
    args = parser.parse_args()

    if os.path.isfile(args.file):
        sys.exit('Error: output file already exists!')

    out_file = open(args.file, 'w')

    apache_git = 'https://git.apache.org/'

    resp = requests.get(apache_git)

    pattern = re.compile(r'<td>(.+)</td>\s*'
                         r'<td>\s*<a href="(.+)">.+</a>\s*</td>\s*'
                         r'<td>\s*<a href="(https://github\.com/.+)">')

    for match in pattern.finditer(resp.text):
        name = match.group(1)
        apache_repo = match.group(2)
        github_repo = match.group(3)
        print(name, apache_repo, github_repo, sep=',', file=out_file)

    out_file.close()


if __name__ == '__main__':
    main()
