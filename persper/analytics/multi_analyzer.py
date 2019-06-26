import os
import json
import pickle
import logging
from git import Repo
from enum import Enum
from Naked.toolshed.shell import muterun_rb
from persper.util.path import root_path
from persper.analytics.c import CGraphServer
from persper.analytics.cpp import CPPGraphServer
from persper.util.normalize_score import normalize_with_coef
from persper.analytics.graph_server import C_FILENAME_REGEXES
from persper.analytics.graph_server import CPP_FILENAME_REGEXES
from persper.analytics.analyzer2 import Analyzer, AnalyzerObserver, emptyAnalyzerObserver


_logger = logging.getLogger(__name__)


class Linguist(Enum):
    """
    Encodes the relationship between a language and its name in linguist's output
    https://github.com/github/linguist/blob/master/lib/linguist/languages.yml
    """
    C = "C"
    CPP = "C++"
    GO = "Go"
    JAVA = "Java"
    JAVASCRIPT = "JavaScript"
    TYPESCRIPT = "TypeScript"
    VUE = "Vue"


class MultiAnalyzer:

    LANGUAGE_THRESHOLD = 0.3

    def __init__(self, repo_path):
        self._repo_path = repo_path
        self._repo = Repo(repo_path)
        self._observer: AnalyzerObserver = emptyAnalyzerObserver
        self._linguist = {}
        self._analyzers = {}
        self._set_linguist()
        self._set_analyzers()

    def _set_linguist(self):
        response = muterun_rb(os.path.join(root_path, 'persper', 'util', 'linguist.rb'), self._repo_path)

        if response.exitcode == 0:
            lang_dict = json.loads(response.stdout)
            total_lines = sum(lang_dict.values())

            for k in lang_dict.keys():
                lang_dict[k] = lang_dict[k] * 1.0 / total_lines

            js = Linguist.JAVASCRIPT.value
            ts = Linguist.TYPESCRIPT.value
            vue = Linguist.VUE.value

            _logger.info(lang_dict)
            if vue in lang_dict:
                _logger.info("Merging Vue to Javascript...")
                if js not in lang_dict:
                    lang_dict[js] = 0
                lang_dict[js] += lang_dict[vue]
                del lang_dict[vue]
                _logger.info(lang_dict)

            if ts in lang_dict:
                _logger.info("Merging TypeScript to JavaScript...")
                if js not in lang_dict:
                    lang_dict[js] = 0
                lang_dict[js] += lang_dict[ts]
                del lang_dict[ts]
                _logger.info(lang_dict)

            # intersect with what languages we support
            for lang, value in lang_dict.items():
                if lang in self._supported_analyzers().keys():
                    self._linguist[lang] = value

            _logger.info(self._linguist)

        else:
            _logger.info('Analyzing Language Error from Linguist')

    def _set_analyzers(self):
        for language, value in self._linguist.items():
            if value > self.__class__.LANGUAGE_THRESHOLD and (language not in self._analyzers.keys()):
                self._analyzers[language] = self._supported_analyzers(language)

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

    def _supported_analyzers(self, language=None):
        analyzers = {
            'C': Analyzer(self._repo_path, CGraphServer(C_FILENAME_REGEXES), firstParentOnly=True),
            'C++': Analyzer(self._repo_path, CPPGraphServer(CPP_FILENAME_REGEXES), firstParentOnly=True)
        }

        if language:
            return analyzers[language]
        else:
            return analyzers


def _is_merged_commit(commit):
    if len(commit.parents) > 1:
        return True
    else:
        return False
