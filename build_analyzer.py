import sys
import json
import pickle
from datetime import datetime, timedelta
from Naked.toolshed.shell import muterun_rb
from persper.analytics.cpp import CPPGraphServer
from persper.analytics.analyzer import Analyzer
from persper.analytics.graph_server import CPP_FILENAME_REGEXES

ALPHA = 0.85
LANGUAGE_LIST = ['C', 'C++']


def build_analyzer(repo_url, pickle_path, repo_path):

    linguist = check_linguist(repo_path)
    major_language = max(linguist, key=linguist.get)

    # Fake data for testing
    major_language = 'C++'
    if major_language in LANGUAGE_LIST:
        az = Analyzer(repo_path, CPPGraphServer(CPP_FILENAME_REGEXES))
        az.analyze(repo_url, pickle_path, from_beginning=True, into_branches=True)
        return pickle_path
    else:
        return None


def check_linguist(repo_path):
    response = muterun_rb('tools/linguist.rb', repo_path)

    if response.exitcode == 0:
        lang_dict = json.loads(response.stdout)
        total_lines = sum(lang_dict.values())

        for k in lang_dict.keys():
            lang_dict[k] = lang_dict[k] * 1.0 / total_lines

        return lang_dict
    else:
        return None

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
        if commit.hexsha in commit_share:
            date = datetime.fromtimestamp(commit.authored_date).date()
            if date in shares:
                shares[date] += commit_share[commit.hexsha]
            else:
                shares[date] = commit_share[commit.hexsha]

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
