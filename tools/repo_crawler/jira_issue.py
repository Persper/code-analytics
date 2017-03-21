#!/usr/bin/env python
# -*- coding:utf-8 -*-

import sys
import urllib

_URL_PREFIX_XML = "https://issues.apache.org/jira/si/jira.issueviews:issue-xml/"
_URL_SUFFIX_XML = ".xml"

class JiraIssue:
    def __init__(self,
                 url_prefix=_URL_PREFIX_XML,
                 url_suffix=_URL_SUFFIX_XML):
        self.url_prefix = url_prefix
        self.url_suffix = url_suffix

    def download(self, issue_id, file_path):
        url = self.url_prefix + issue_id + "/" + issue_id + self.url_suffix
        try:
            print urllib.urlretrieve(url, file_path)[0]
        except Exception as e:
            print "[Error] JiraIssue.download: ", type(e), e

if __name__ == "__main__":
    if len(sys.argv) != 3:
        print sys.argv[0] + " ISSUE_ID FILE_PATH"
        sys.exit(1)
    jira_issue = JiraIssue()
    jira_issue.download(sys.argv[1], sys.argv[2]);
