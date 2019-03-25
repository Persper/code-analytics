import os
import yaml
from pathlib import Path
from datetime import datetime, timedelta
from persper.analytics.analyzer2 import Analyzer
from persper.analytics.c import CGraphServer
from persper.analytics.go import GoGraphServer
from persper.analytics.cpp import CPPGraphServer
from persper.analytics.java import JavaGraphServer
from persper.analytics.graph_server import C_FILENAME_REGEXES
from persper.analytics.graph_server import GO_FILENAME_REGEXES
from persper.analytics.graph_server import CPP_FILENAME_REGEXES
from persper.analytics.graph_server import JAVA_FILENAME_REGEXES


def get_config_from_yaml(config_path):
    with open(config_path, 'r') as f:
        yaml_config = yaml.safe_load(f)

    return yaml_config


LANGUAGE_LIST = ['C', 'C++', 'Java', 'Go']
LANGUAGE_THRESHOLD = 0.3
root_path = os.path.dirname(os.path.abspath(__file__))
config = get_config_from_yaml(os.path.join(root_path, 'config.yaml'))


def get_top_commits(commits, commit_share):
    top_commits = []
    for commit in commits:
        if commit.hexsha in commit_share:
            share_value = commit_share[commit.hexsha]
            top_commits.append({
                'author_email': commit.author.email,
                'author_name': commit.author.name,
                'author_timestamp': commit.authored_date,
                'committer_email': commit.committer.email,
                'committer_name': commit.committer.name,
                'commit_timestamp': commit.committed_date,
                'hash': commit.hexsha,
                'parent_hashes': [p.hexsha for p in commit.parents],
                'dev_value': share_value,
                'title': commit.message.splitlines()[0],
                'message': commit.message
            })

    top_commits = sorted(top_commits, key=lambda k: k['dev_value'], reverse=True)[:10]

    return top_commits


def daterange(start_date, end_date):
    for n in range(int((end_date - start_date).days) + 1):
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


def modules_contribution(ccgraph, coef, email=None, alpha=0.85, black_set=None):
    if black_set is None:
        black_set = []
    if email is None:
        graph_commits = list(ccgraph.commits().values())
        commits = [commit['hexsha'] for commit in graph_commits]
    else:
        graph_commits = list(ccgraph.commits().values())
        commits = [commit['hexsha'] for commit in graph_commits if commit['authorEmail'] == email]

    modules_share = {}
    func_devranks = ccgraph.function_devranks(alpha, black_set)

    for func, data in ccgraph.nodes(data=True):
        size = data['size']
        history = data['history']
        files = data['files']

        if len(history) == 0:
            continue

        for cid, chist in history.items():
            csize = chist['adds'] + chist['dels']
            sha = ccgraph.commits()[cid]['hexsha']
            if (sha not in black_set) and (sha in commits):
                dr = (csize / size) * func_devranks[func]
                for file in files:
                    if file in modules_share:
                        modules_share[file] += dr / len(files) * 1.0 * coef
                    else:
                        modules_share[file] = dr / len(files) * 1.0 * coef

    return modules_share


def get_aggregated_modules_on_dev(aggregated_modules, dev_modules, normalize_coef):
    aggregated_dev_modules = {}

    for path, value in dev_modules.items():
        new_path = get_aggregated_path(path, aggregated_modules)

        normalized_value = value / normalize_coef

        if new_path in aggregated_dev_modules:
            aggregated_dev_modules[new_path] += normalized_value
        else:
            aggregated_dev_modules[new_path] = normalized_value

    return aggregated_dev_modules


def get_aggregated_path(path, aggregated_modules):
    if path == '.':
        return '...'

    if path in aggregated_modules:
        return path
    elif (path + "/...") in aggregated_modules:
        return path + "/..."
    else:
        return get_aggregated_path(str(Path(path).parent), aggregated_modules)


def is_merged_commit(commit):
    if len(commit.parents) > 1:
        return True
    else:
        return False


def supportted_analyzer(repo_path, language):
    supportted_analyzers = {
        'C': Analyzer(repo_path, CGraphServer(C_FILENAME_REGEXES)),
        'C++': Analyzer(repo_path, CPPGraphServer(CPP_FILENAME_REGEXES)),
        'Go': Analyzer(repo_path, GoGraphServer(config['go_server_addr'], GO_FILENAME_REGEXES)),
        'Java': Analyzer(repo_path, JavaGraphServer(JAVA_FILENAME_REGEXES))
    }

    return supportted_analyzers[language]


