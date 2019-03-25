import os
import json
import pickle
from git import Repo
from pathlib import Path
from datetime import datetime, timedelta
from Naked.toolshed.shell import muterun_rb
from vdev.utils import get_config_from_yaml
from persper.analytics.c import CGraphServer
from persper.analytics.score import normalize
from persper.analytics.go import GoGraphServer
from persper.analytics.cpp import CPPGraphServer
from persper.analytics.java import JavaGraphServer
from vdev.component_aggregation import get_aggregated_modules
from persper.analytics.graph_server import C_FILENAME_REGEXES
from persper.analytics.graph_server import GO_FILENAME_REGEXES
from persper.analytics.graph_server import CPP_FILENAME_REGEXES
from persper.analytics.graph_server import JAVA_FILENAME_REGEXES
from persper.analytics.analyzer2 import Analyzer, AnalyzerObserver, emptyAnalyzerObserver


LANGUAGE_LIST = ['C', 'C++', 'Java', 'Go']
root_path = os.path.dirname(os.path.abspath(__file__))


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


config = get_config_from_yaml(os.path.join(root_path, 'config.yaml'))


def supportted_analyzer(repo_path, language):
    supportted_analyzers = {
        'C': Analyzer(repo_path, CGraphServer(C_FILENAME_REGEXES)),
        'C++': Analyzer(repo_path, CPPGraphServer(CPP_FILENAME_REGEXES)),
        'Go': Analyzer(repo_path, GoGraphServer(config['go_server_addr'], GO_FILENAME_REGEXES)),
        'Java': Analyzer(repo_path, JavaGraphServer(JAVA_FILENAME_REGEXES))
    }

    return supportted_analyzers[language]


class VdevAnalyzer:

    def __init__(self, repo_path, new_pickle_path=None):
        self._repo_path = repo_path
        self._repo = Repo(repo_path)
        self._observer: AnalyzerObserver = emptyAnalyzerObserver
        self._analyzers = {}
        self._linguist = {}
        self.check_linguist()
        self.set_analyzers()
        self.saved_path = new_pickle_path

    def check_linguist(self):
        response = muterun_rb(os.path.join(root_path, 'linguist.rb'), self._repo_path)

        if response.exitcode == 0:
            lang_dict = json.loads(response.stdout)
            total_lines = sum(lang_dict.values())

            for k in lang_dict.keys():
                lang_dict[k] = lang_dict[k] * 1.0 / total_lines

            for lang, value in lang_dict.items():
                if lang in LANGUAGE_LIST:
                    self._linguist[lang] = value

            print(self._linguist)

        else:
            print('Analyzing Language Error')

    def set_analyzers(self):
        for language, value in self._linguist.items():
            if value > 0.05 and (language not in self._analyzers.keys()):
                self._analyzers[language] = {
                    'az': supportted_analyzer(self._repo_path, language),
                    'graph': supportted_analyzer(self._repo_path, language).graph
                }

        print(self._analyzers)

    async def analyzing(self):
        for language, analyzer in self._analyzers.items():    
            print('start analyzing language, ', language)
            print(analyzer['az'].originCommit)
            analyzer['az']._graphServer.set_graph(analyzer['graph'])
            await analyzer['az'].analyze()
            analyzer['az'].originCommit = analyzer['az'].terminalCommit
            analyzer['graph'] = analyzer['az'].graph

        self.save()

    def module_contrib(self, dev_share):
        all_modules = {}

        for key, analyzer in self._analyzers.items():
            all_modules.update(modules_contribution(analyzer['graph'], self._linguist[key]))

        aggregated_modules = get_aggregated_modules(all_modules)
        normalize_coef = sum(aggregated_modules.values())
        if normalize_coef == 0:
            normalize_coef = 1.0

        for email in dev_share.keys():
            dev_modules = {}
            for lang, analyzer in self._analyzers.items():
                dev_modules.update(modules_contribution(analyzer['graph'], self._linguist[lang], email))

            dev_share[email]['modules'] = get_aggregated_modules_on_dev(aggregated_modules, dev_modules, normalize_coef)
        return dev_share

    def project_commit_share(self, alpha=0.85):
        overall_commit_share = {}

        for key, analyzer in self._analyzers.items():
            commit_share = normalize(analyzer['graph'].commit_devranks(alpha), self._linguist[key])

            for commit, value in commit_share.items():
                if key in overall_commit_share:
                    overall_commit_share[commit] += value
                else:
                    overall_commit_share[commit] = value

        return normalize(overall_commit_share)

    def developer_profile(self, alpha=0.85, show_merge=True):
        dev_share = {}

        commit_share = self.project_commit_share(alpha)

        for commit in self._repo.iter_commits():

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

        dev_share = self.module_contrib(dev_share)

        return dev_share

    def save(self):
        if self.saved_path:
            print('Saving pickle file')
            with open(self.saved_path, 'wb+') as f:
                pickle.dump(self, f)

    def basic_stats(self, alpha=0.85, show_merge=True):
        commit_share = self.project_commit_share(alpha)
        points = []
        for commit in self._repo.iter_commits():

            if is_merged_commit(commit) and not show_merge:
                continue

            if commit.hexsha in commit_share:
                points.append(commit_share[commit.hexsha])
            else:
                points.append(0.0)

        return list(reversed(points))
