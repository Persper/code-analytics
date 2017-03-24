#!/usr/bin/env python
# -*- coding: utf-8 -*-

import argparse
import dicttoxml
import github3
import xml.etree.ElementTree as ET

class GitHubComments:
    def __init__(self, user = None, password = None):
        self.gh = github3.login(user, password)

    def login(self, user, password):
        self.gh = github3.login(user, password)

    def download(self, user, repo, num, file_path):
        pr = self.gh.pull_request(user, repo, num)
        comments = ET.Element('comments')
        for comment in pr.issue_comments():
            xml_snippet = dicttoxml.dicttoxml(comment.as_dict(),
                                              attr_type=False,
                                              custom_root='comment')
            comments.append(ET.fromstring(xml_snippet))
        for comment in pr.review_comments():
            xml_snippet = dicttoxml.dicttoxml(comment.as_dict(),
                                              attr_type=False,
                                              custom_root='comment')
            comments.append(ET.fromstring(xml_snippet))
        return ET.ElementTree(comments).write(file_path, encoding="utf-8")

def add_args(parser):
    parser.add_argument('-u', '--github-user',
                        help='user name of a GitHub account',
                        type=str, required=True)
    parser.add_argument('-p', '--github-password',
                        help='password of a GitHub account',
                        type=str, required=True)

def main():
    parser = argparse.ArgumentParser()
    add_args(parser)
    args = parser.parse_args()

    ghc = GitHubComments(args.github_user, args.github_password)
    ghc.download('apache', 'spark', 15220, 'temp.xml')

if __name__ == '__main__':
    main()
