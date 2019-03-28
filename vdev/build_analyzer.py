import os
import json
import pickle
from datetime import datetime, timedelta
from Naked.toolshed.shell import muterun_rb
from persper.analytics.cpp import CPPGraphServer
from persper.analytics.c import CGraphServer
from persper.analytics.analyzer import Analyzer
from persper.analytics.go import GoGraphServer
from persper.analytics.score import normalize
from persper.analytics.graph_server import CPP_FILENAME_REGEXES
from persper.analytics.graph_server import C_FILENAME_REGEXES
from persper.analytics.graph_server import GO_FILENAME_REGEXES
from pathlib import Path
from vdev.utils import get_config_from_yaml
from vdev.analyzer_observer_vdev import AnalyzerObserverVdev
from vdev.component_aggregation import get_aggregated_modules


root_path = os.path.dirname(os.path.abspath(__file__))
config = get_config_from_yaml(os.path.join(root_path, 'config.yaml'))
LANGUAGE_LIST = ['C', 'C++', 'Go']


def observer(redis_address, redis_port, git_url):
    return AnalyzerObserverVdev(redis_address, redis_port, git_url)


async def build_analyzer2(git_url, repo_path, original_pickle_path, new_pickle_path):
    linguist = check_linguist(repo_path)
    major_language = max(linguist, key=linguist.get)
    print('The major language is: ', major_language)

    if major_language not in LANGUAGE_LIST:
        return

    if original_pickle_path and os.path.exists(original_pickle_path):
        az = pickle.load(open(original_pickle_path, 'rb'))
        az.observer = observer(config['redis']['host'], config['redis']['port'], git_url)
        await az.analyze(new_pickle_path, continue_iter=True, end_commit_sha='HEAD', into_branches=True)
        return

    analyzer_dict = {
        'C':   Analyzer(repo_path, CGraphServer(C_FILENAME_REGEXES)),
        'C++': Analyzer(repo_path, CPPGraphServer(CPP_FILENAME_REGEXES)),
        'Go':  Analyzer(repo_path, GoGraphServer(config['go_server_addr'], GO_FILENAME_REGEXES))
    }

    az = analyzer_dict[major_language]
    az.observer = observer(config['redis']['host'], config['redis']['port'], git_url)
    await az.analyze(new_pickle_path, from_beginning=True, into_branches=True)


async def build_analyzer(git_url, repo_path, original_pickle_path, new_pickle_path):
    linguist = check_linguist(repo_path)
    major_language = max(linguist, key=linguist.get)
    print('The major language is: ', major_language)

    if major_language in LANGUAGE_LIST:
        # Todo: Choose the right server to do analyzing based on linguist
        if original_pickle_path and os.path.exists(original_pickle_path):
            az = pickle.load(open(original_pickle_path, 'rb'))
            az.observer = observer(config['redis']['host'], config['redis']['port'], git_url)
            await az.analyze(new_pickle_path, continue_iter=True, end_commit_sha='HEAD', into_branches=True)
        else:
            az = Analyzer(repo_path, CPPGraphServer(CPP_FILENAME_REGEXES))
            az.observer = observer(config['redis']['host'], config['redis']['port'], git_url)
            await az.analyze(new_pickle_path, from_beginning=True, into_branches=True)


def check_linguist(repo_path):
    response = muterun_rb(os.path.join(root_path, 'linguist.rb'), repo_path)

    if response.exitcode == 0:
        lang_dict = json.loads(response.stdout)
        total_lines = sum(lang_dict.values())

        for k in lang_dict.keys():
            lang_dict[k] = lang_dict[k] * 1.0 / total_lines

        return lang_dict
    else:
        print('Analyzing Language Error')
        return {}


def basic_stats(pickle_path, alpha=0.5, show_merge=True):
    az = pickle.load(open(pickle_path, 'rb'))

    commit_share = normalize(az.get_graph().commit_devranks(alpha, black_set=[]))

    points = []

    for commit in az._ri.repo.iter_commits():

        if is_merged_commit(commit) and not show_merge:
            continue

        if commit.hexsha in commit_share:
            points.append(commit_share[commit.hexsha])
        else:
            points.append(0.0)

    return list(reversed(points))


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


def developer_profile(pickle_path, alpha=0.5, show_merge=True):
    dev_share = {}
    az = pickle.load(open(pickle_path, 'rb'))

    commit_share = normalize(az.get_graph().commit_devranks(alpha, black_set=[]))

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
        item['top_commits'] = get_top_commits(item['commits'], commit_share)

    dev_share = module_contrib(az.get_graph(), dev_share)

    return dev_share


def module_contrib(ccgraph, dev_share):
    all_modules = modules_on_devs(ccgraph)
    aggregated_modules = get_aggregated_modules(all_modules)

    normalize_coef = sum(aggregated_modules.values())

    if normalize_coef == 0:
        normalize_coef = 1.0

    print('normalize_coef')
    print(normalize_coef)

    for email in dev_share.keys():
        dev_modules = modules_on_devs(ccgraph, email)
        dev_share[email]['modules'] = get_aggregated_modules_on_dev(aggregated_modules, dev_modules, normalize_coef)

    return dev_share


def modules_on_devs(ccgraph, email=None, alpha=0.5, black_set=[]):
    if email==None:
        graph_commits = list(ccgraph.commits().values())
        commits = [commit['hexsha'] for commit in graph_commits]
    else:
        graph_commits  = list(ccgraph.commits().values())
        commits =  [commit['hexsha'] for commit in graph_commits if commit['authorEmail'] == email]

    modules_share = {}
    func_devranks = ccgraph.function_devranks(alpha, black_set=black_set)

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
                        modules_share[file] += dr/len(files)*1.0
                    else:
                        modules_share[file] = dr/len(files)*1.0

    return modules_share


def get_aggregated_modules_on_dev(aggregated_modules, dev_modules, normalize_coef):
    new_modules = {}

    for path, value in dev_modules.items():
        new_path = get_aggregated_path(path, aggregated_modules)

        normalized_value = value / normalize_coef

        if new_path in new_modules:
            new_modules[new_path] += normalized_value
        else:
            new_modules[new_path] = normalized_value

    return new_modules


def get_aggregated_path(path, aggregated_modules):
    if path == '.':
        return '...'

    if path in aggregated_modules:
        return path
    elif (path + "/...") in aggregated_modules:
        return (path + "/...")
    else:
        return get_aggregated_path(str(Path(path).parent), aggregated_modules)


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
            
    top_commits = sorted(top_commits, key=lambda k: k['dev_value'],  reverse=True)[:10]

    return top_commits