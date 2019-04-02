import os
import json
import pickle
from git import Repo
from Naked.toolshed.shell import muterun_rb
from persper.analytics.analyzer2 import AnalyzerObserver, emptyAnalyzerObserver
from persper.util.supported_analyzer import supported_analyzer
from persper.util.path import root_path
from persper.util.normalize_score import normalize_with_coef


LANGUAGE_LIST = ['C', 'C++']
LANGUAGE_THRESHOLD = 0.3


class MultiAnalyzer:

    def __init__(self, repo_path):
        self._repo_path = repo_path
        self._repo = Repo(repo_path)
        self._observer: AnalyzerObserver = emptyAnalyzerObserver
        self._linguist = {}
        self._analyzers = {}
        self.set_linguist()
        self.set_analyzers()

    def set_linguist(self):
        response = muterun_rb(os.path.join(root_path, 'persper', 'util', 'linguist.rb'), self._repo_path)

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
            print('Analyzing Language Error from Linguist')

    def set_analyzers(self):
        for language, value in self._linguist.items():
            if value > LANGUAGE_THRESHOLD and (language not in self._analyzers.keys()):
                self._analyzers[language] = supported_analyzer(self._repo_path, language)

        print(self._analyzers)

    async def analyzing(self, saved_path=None):
        for language, analyzer in self._analyzers.items():    
            print('Start Analyzing Language, ', language)
            analyzer.terminalCommit = analyzer._repo.head.commit
            await analyzer.analyze()

        self.save(saved_path)

    def project_commit_share(self, alpha=0.5):
        overall_commit_share = {}

        for key, analyzer in self._analyzers.items():
            commit_share = normalize_with_coef(analyzer.graph.commit_devranks(alpha), self._linguist[key])

            for commit, value in commit_share.items():
                if key in overall_commit_share:
                    overall_commit_share[commit] += value
                else:
                    overall_commit_share[commit] = value

        return normalize_with_coef(overall_commit_share)

    def save(self, saved_path=None):
        if saved_path:
            print('Saving pickle file to:', saved_path)
            with open(saved_path, 'wb+') as f:
                pickle.dump(self, f)
        else:
            print('No pickle file saved')

    def basic_stats(self, alpha=0.5, show_merge=True):
        commit_share = self.project_commit_share(alpha)
        points = []
        for commit in self._repo.iter_commits():

            if _is_merged_commit(commit) and not show_merge:
                continue

            if commit.hexsha in commit_share:
                points.append(commit_share[commit.hexsha])
            else:
                points.append(0.0)

        return list(reversed(points))


def _is_merged_commit(commit):
    if len(commit.parents) > 1:
        return True
    else:
        return False
