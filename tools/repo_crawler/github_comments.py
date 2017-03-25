#!/usr/bin/env python
# -*- coding: utf-8 -*-

import argparse
import dicttoxml
import github3
import string
import threading
import time
import xml.etree.ElementTree as ET

class GitHubComments:
    def __init__(self, user = None, password = None, limit_per_min=81):
        self.gh = github3.login(user, password)
        self._limit_per_min = limit_per_min

        self._lock = threading.Lock()
        self._last_time = time.time()
        self._rest = limit_per_min

    def login(self, user, password):
        self.gh = github3.login(user, password)

    def get_lease(self):
        with self._lock:
            if self._rest > 0:
                self._rest -= 1
                return True
            elif time.time() - self._last_time > 60:
                self._rest = self._limit_per_min - 1
                self._last_time = time.time()
                return True
            else:
                return False

    def download(self, user, repo, num, file_path):
        while not self.get_lease():
            time.sleep(5)
        pr = self.gh.pull_request(user, repo, num)
        comments = ET.Element('comments')
        for comment in pr.issue_comments():
            snippet = dicttoxml.dicttoxml(comment.as_dict(),
                                          attr_type=False,
                                          custom_root='comment')
            snippet = ''.join(x for x in snippet if x in string.printable)
            comments.append(ET.fromstring(snippet))
        for comment in pr.review_comments():
            snippet = dicttoxml.dicttoxml(comment.as_dict(),
                                              attr_type=False,
                                              custom_root='comment')
            snippet = ''.join(x for x in snippet if x in string.printable)
            comments.append(ET.fromstring(snippet))
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
    ghc.download('apache', 'spark', 8060, '8060.xml')
    ghc.download('apache', 'spark', 8069, '8069.xml')

if __name__ == '__main__':
    main()
