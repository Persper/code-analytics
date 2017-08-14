import os
import sys
import time
import urllib

_URL_PREFIX_XML = "https://issues.apache.org/jira/si/jira.issueviews:issue-xml/"
_URL_SUFFIX_XML = ".xml"

class JiraIssue:
    def __init__(self,
                 url_prefix=_URL_PREFIX_XML,
                 url_suffix=_URL_SUFFIX_XML):
        self.url_prefix = url_prefix
        self.url_suffix = url_suffix

    def download(self, issue_id, dir_path, file_name):
        url = self.url_prefix + issue_id + "/" + issue_id + self.url_suffix
        file_path = os.path.join(dir_path, file_name)
        invalid_path = os.path.join(dir_path, ".invalid." + file_name)
        if os.path.isfile(file_path) or os.path.isfile(invalid_path):
            return
        for i in range(3):
            try:
                print urllib.urlretrieve(url, file_path)[0]
                with open(file_path, 'r') as downloaded:
                    if "<h1>Oops, you&#39;ve found a dead link.</h1>" in \
                            downloaded.read():
                        os.rename(file_path, invalid_path)
                        print "Invalid issue ID:", invalid_path
                break
            except Exception as e:
                if i == 2:
                    print "[Error] JiraIssue.download: ", type(e), e
                else:
                    time.sleep(10)

if __name__ == "__main__":
    if len(sys.argv) != 3:
        print sys.argv[0] + " ISSUE_ID FILE_PATH"
        sys.exit(1)
    jira_issue = JiraIssue()
    jira_issue.download(sys.argv[1], sys.argv[2]);
