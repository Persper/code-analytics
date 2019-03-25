import json
import pickle
from git import Repo
from Naked.toolshed.shell import muterun_rb
from vdev.component_aggregation import get_aggregated_modules
from persper.analytics.analyzer2 import AnalyzerObserver, emptyAnalyzerObserver
from vdev.utils import *


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
            if value > LANGUAGE_THRESHOLD and (language not in self._analyzers.keys()):
                self._analyzers[language] = dict(az=supportted_analyzer(self._repo_path, language),
                                                 graph=supportted_analyzer(self._repo_path, language).graph)

        print(self._analyzers)

    async def analyzing(self):
        for language, analyzer in self._analyzers.items():    
            print('Start analyzing language, ', language)
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
            commit_share = normalize_with_coef(analyzer['graph'].commit_devranks(alpha), self._linguist[key])

            for commit, value in commit_share.items():
                if key in overall_commit_share:
                    overall_commit_share[commit] += value
                else:
                    overall_commit_share[commit] = value

        return normalize_with_coef(overall_commit_share)

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
