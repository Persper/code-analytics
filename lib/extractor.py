# coding: utf-8
import xml.dom.minidom
import re
import os
import sys
import pickle

class JiraIssueExtractor():
    def __init__(self):
        self.datasets = {}
        
    # Remove useless information from a jira issue file
    def remove_useless_data(self, data):
        data = re.sub(r'</?p>', "", data)
        data = re.sub(r'</?tt>', "", data)
        data = re.sub(r'<br/>', "", data)
        data = re.sub(r'\<a.*?\>', "", data)
        data = re.sub(r'</a>', "", data)
        data = re.sub(r'\<div.*?\>', "", data)
        data = re.sub(r'\</div\>', "", data)
        data = re.sub(r'\<pre.*?\>', "", data)
        data = re.sub(r'\</pre\>', "", data)
        data = re.sub(r'\<span.*?\>', "", data)
        data = re.sub(r'\</span\>', "", data)
        data = re.sub(r'\<ul.*?\>', "", data)
        data = re.sub(r'</ul\>', "", data)
        data = re.sub(r'\<table.*?\>', "", data)
        data = re.sub(r'\</table\>', "", data)
        data = re.sub(r'\<td.*?\>', "", data)
        data = re.sub(r'\</td\>', "", data)
        data = re.sub(r'\<th.*?\>', "", data)
        data = re.sub(r'\</th\>', "", data)
        data = re.sub(r'\</?del\>', "", data)
        data = re.sub(r'\</?em\>', "", data)
        data = re.sub(r'\</?h3\>', "", data)
        data = re.sub(r'\</?li\>', "", data)
        data = re.sub(r'</?ol>', "", data)
        data = re.sub(r'</?tr>', "", data)
        data = re.sub(r'</?tbody>', "", data)
        data = re.sub(r'\<img.*?\>', "", data)
        data = re.sub(r'\n', " ", data)
        data = re.sub(r'\&gt\;', ">", data)
        data = re.sub(r'\&lt\;', "<", data)
        data = re.sub(r'\&\#91\;', "[", data)
        data = re.sub(r'\&\#93\;', "]", data)
        data = re.sub(r'\&\#8211\;', "-", data)
        data = re.sub(r'\&amp\;', "&", data)
        data = re.sub(r'\<200c\>', "", data)
        data = re.sub(r'\<200b\>', "", data)
        return data

    # Read the useful information from a Jira issue file (Title, Description, Comments, Type, Priority)
    def read_data_from_jira_file(self, parseFile, issueId):
        """return dataset, a list of dict data points"""
        dp = {}
        dp['issue'] = issueId

        title = parseFile.getElementsByTagName('title')
        data = title[1].firstChild.data
        data = re.sub(r'\[.*?\]\s', "", data)
        data = self.remove_useless_data(data)
        dp['title'] = data

        description = parseFile.getElementsByTagName('description')
        des_str = ''
        for i, des in enumerate(description):
            if i != 0 and des.firstChild != None:
                data = self.remove_useless_data(des.firstChild.data)
                des_str = des_str + data
        dp['description'] = des_str

        comments = parseFile.getElementsByTagName('comment')
        comment_str = ''
        for i, com in enumerate(comments):
            if com.firstChild:
                data = self.remove_useless_data(com.firstChild.data)
                comment_str = comment_str + data
        dp['comment'] = comment_str 

        type = parseFile.getElementsByTagName('type')
        dp['type'] = type[0].firstChild.data

        priority = parseFile.getElementsByTagName('priority')
        for i, pri in enumerate(priority):
            dp['priority'] = pri.firstChild.data

        return dp

    # Read all useful information from all files under a jira issues dir
    # Each issue data structure : (issue id) -> (title, description, comments, priority, type)
    def generate_dataset(self, filepath):
        dataset = {}
        allFiles =  os.listdir(filepath)
        invalidName = "invalid"
        numFiles = 0
        for eachFile in allFiles:
            if 'GitHub' not in eachFile:
                if invalidName in eachFile:
                    continue
                arr = re.split('-|\.', eachFile)
                fromFile = os.path.join('%s%s' % (filepath, eachFile))
                dom = xml.dom.minidom.parse(fromFile)
                parseFile = dom.documentElement
                dp = self.read_data_from_jira_file(parseFile, arr[2])

                if arr[2] in dataset.keys():
                    dataset[arr[2]]['title'] = dataset[arr[2]]['title'] + dp['title'] 
                    dataset[arr[2]]['description'] = dataset[arr[2]]['description'] + dp['description']
                    dataset[arr[2]]['comment'] = dataset[arr[2]]['comment'] + dp['comment'] 
                    #if dataset[arr[2]]['type'] not in dp['type']:
                    #    print (dataset[arr[2]]['type'], dp['type'])
                    #if dataset[arr[2]]['priority'] not in dp['priority']:
                    #    print (dataset[arr[2]]['type'], dp['type'])
                else:
                    dataset.update({arr[2]:dp})
                numFiles += 1
        #print (numFiles)
        return dataset

    # Remove jira issues which has no description, comments and priority
    def remove_uncomplete_issues(self, project_set, datasets):
        for project in project_set:
            keys = list(datasets[project].keys())  
            for issueId in keys:
                issue = datasets[project][issueId]
                if 'description' not in issue:
                    datasets[project].pop(issueId)
                elif 'comment' not in issue:
                    datasets[project].pop(issueId)
                elif 'priority' not in issue:
                    datasets[project].pop(issueId)

    # Dump the dataset into pickle file
    def dump_into_pickle(self, datasets, filePath):
        pickle.dump(datasets, open(filePath, 'wb'), True)



class FSPatchExtractor():
    def __init__(self):
        self.datasets = {}

    def generate_dataset(self, files):
        """return dataset, a list of dict data points"""
        dataset = []
        attributes = ('type', 'sub_type', 'sub_sub_type', 
                      'cons_type', 'sub_cons_type')

        re_patch_bp = re.compile("""\((?P<type>[bp]):
                                    (?P<sub_type>[^(->)]*)
                                    (->(?P<sub_sub_type>[^(->)\)]*))?
                                    (->[^(->)\)]*)*\):
                                    \(s:(?P<cons_type>[^(->)]*)
                                    (->(?P<sub_cons_type>[^\)]*))?\)""", re.VERBOSE)
        re_patch_c = re.compile("""\((?P<type>c):
                                    (?P<sub_type>[^(->)]*)
                                    (->(?P<sub_sub_type>[^(->)\)]*))?\)""", re.VERBOSE)
        re_patch_misc = re.compile("""\((?P<type>misc)->
                                        (?P<sub_type>[^\)]*)\)""", re.VERBOSE)
        re_patch_f = re.compile("\((?P<type>f)\)")

        for fname in files:
            with open(fname, 'r') as f:
                lines = f.readlines()

            ptr = 0
            while ptr <= len(lines) - 2:
                line = lines[ptr]
                next_line = lines[ptr + 1]
                if line.startswith(' ') or line.startswith('\t'):
                    try:
                        assert(next_line.lstrip().startswith('.'))
                    except:
                        """
                        print('-------- Error line ---------')
                        print('line:%s' % line)
                        print('next:%s' % next_line)
                        print('-----------------------------')
                        """
                        ptr += 1
                        continue
                    dp = {}
                    dp['subject'] = line.lstrip().rstrip()

                    m = re_patch_bp.search(next_line) or \
                        re_patch_c.search(next_line) or \
                        re_patch_misc.search(next_line) or \
                        re_patch_f.search(next_line)
                    if m != None:
                        gd = m.groupdict()
                        for attr in attributes:
                            if attr in gd:
                                dp[attr] = gd[attr]
                        dataset.append(dp)
                        ptr += 2
                    else:
                        # skip lines with multiple sub_types and consequences
                        ptr += 1
                else:
                    ptr += 1

        return dataset
