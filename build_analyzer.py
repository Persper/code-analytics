import sys
import os
import json
import pickle
from datetime import datetime, timedelta
from Naked.toolshed.shell import muterun_rb
from persper.analytics.cpp import CPPGraphServer
from persper.analytics.analyzer import Analyzer
from persper.analytics.graph_server import CPP_FILENAME_REGEXES

ALPHA = 0.85
LANGUAGE_LIST = ['C', 'C++']


def build_analyzer(repo_url, repo_path, original_pickle_path, new_pickle_path):

    linguist = check_linguist(repo_path)
    major_language = max(linguist, key=linguist.get)
    print('The major language is: ', major_language)

    if major_language in LANGUAGE_LIST:
        # Todo: Choose the right server to do analyzing based on linguist
        if os.path.exists(original_pickle_path):
            az = pickle.load(open(original_pickle_path, 'rb'))
            az.analyze(repo_url, new_pickle_path, continue_iter=True, end_commit_sha='master', into_branches=True)
        else:
            az = Analyzer(repo_path, CPPGraphServer(CPP_FILENAME_REGEXES))
            az.analyze(repo_url, new_pickle_path, from_beginning=True, into_branches=True)


def check_linguist(repo_path):
    root_path = os.path.dirname(os.path.abspath(__file__))
    response = muterun_rb(os.path.join(root_path, 'tools/linguist.rb'), repo_path)

    if response.exitcode == 0:
        lang_dict = json.loads(response.stdout)
        total_lines = sum(lang_dict.values())

        for k in lang_dict.keys():
            lang_dict[k] = lang_dict[k] * 1.0 / total_lines

        return lang_dict
    else:
        print('Analyzing Language Error')
        return {}

def basic_stats(pickle_path, alpha=0.85, show_merge=True):
    az = pickle.load(open(pickle_path, 'rb'))

    commit_share = az.get_graph().commit_devranks(alpha, black_set=[])
    points = []
    

    for commit in az._ri.repo.iter_commits():

        if is_merged_commit(commit) and not show_merge:
            continue

        if commit.hexsha in commit_share:
            points.append(commit_share[commit.hexsha])
        else:
            points.append(0.0)

    return points


def is_merged_commit(commit):
    if len(commit.parents) > 1:
        return True
    else:
        return False


def daterange(start_date, end_date):
    for n in range(int((end_date - start_date).days)+1):
        yield start_date + timedelta(n)
    

def share_distribution(commits, commit_share):
    shares = {}
    for commit in commits:
        date = datetime.fromtimestamp(commit.authored_date).date()
        share_value = 0.0
        if commit.hexsha in commit_share:
            share_value = commit_share[commit.hexsha]

        if date in shares:
            shares[date] += share_value
        else:
            shares[date] = share_value

    shares = dict(sorted(shares.items()))
    init_commit_date = list(shares.keys())[0]
    last_commit_date = list(shares.keys())[-1]

    values = []
    for single_date in daterange(init_commit_date, last_commit_date):

        if single_date in shares.keys():
            values.append(shares[single_date])
        else:
            values.append(0.0)

    return init_commit_date, last_commit_date, values


def developer_profile(pickle_path, alpha=0.85, show_merge=True):
    dev_share = {}
    az = pickle.load(open(pickle_path, 'rb'))

    commit_share = az.get_graph().commit_devranks(alpha, black_set=[])

    for commit in az._ri.repo.iter_commits():

        if is_merged_commit(commit) and not show_merge:
            continue

        email = commit.author.email

        if email in dev_share:
            dev_share[email]["commits"].append(commit)
        else:
            dev_share[email] = {}
            dev_share[email]["commits"] = [commit]
            dev_share[email]["email"] = email

    for item in dev_share.values():
        init_commit_date, last_commit_date, values = share_distribution(item['commits'], commit_share)
        
        item['distrib'] = {
            'init_commit_date': init_commit_date,
            'last_commit_date': last_commit_date,
            'values': values
        }
        item['dev_value'] = sum(values)

    return dev_share
