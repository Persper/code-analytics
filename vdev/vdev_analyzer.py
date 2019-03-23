from persper.analytics.analyzer2 import Analyzer

LANGUAGE_LIST = ['C', 'C++', 'Java']

SUPPORTED_ANALYZER = {
    'C':    Analyzer(repo_path, CGraphServer(C_FILENAME_REGEXES)),
    'C++':  Analyzer(repo_path, CPPGraphServer(CPP_FILENAME_REGEXES)),
    'Go':   Analyzer(repo_path, GoGraphServer(config['go_server_addr'], GO_FILENAME_REGEXES)),
    'Java': Analyzer(repo_path, JavaGraphServer(JAVA_FILENAME_REGEXES))
}

class VdevAnalyzer:

    def __init__(self, repo_path, original_pickle_path, new_pickle_path):
        if original_pickle_path:
            self = pickle.load(open(original_pickle_path, 'rb'))
        else:
            self._repo_path = repo_path
            self._repo = Repo(repo_path)
            self._observer: AnalyzerObserver = emptyAnalyzerObserver

        self.linguist = check_linguist(repo_path)
        self.analyzers = set_analyzers(self.linguist)

    def check_linguist(self, repo_path):
        response = muterun_rb(os.path.join(root_path, 'linguist.rb'), self._repo_path)

        if response.exitcode == 0:
            lang_dict = json.loads(response.stdout)
            total_lines = sum(lang_dict.values())

            for k in lang_dict.keys():
                lang_dict[k] = lang_dict[k] * 1.0 / total_lines

            supported_lang_dict = { supported_lang: old_dict[supported_lang] for supported_lang in LANGUAGE_LIST }

            return supported_lang_dict

        else:
            print('Analyzing Language Error')
            return {}

    def set_analyzers(self, linguist, az_list):
        for key, item in self.linguist:
            if az_list[key] is None:
                az_list[key] = SUPPORTED_ANALYZER[key]

        return za_list

    def analyzing(self, new_pickle_path):
        for az in self._ccgraphs:
            az.originCommit = az.terminalCommit
            await az.analyze()

        save(self, new_pickle_path)

    def project_commit_share(self, alpha=0.85):
        project_commit_share = {}

        for key, az in self._ccgraphs:
            commit_share = normalize_with_proportion(az.graph.commit_devranks(alpha), self.linguist[key])

            for key, value in commits.items():
                if key in project_commit_share:
                    project_commit_share[key] += value
                else:
                    project_commit_share[key] = value

        return normalize_with_proportion(project_commit_share)

    def normalize_with_proportion(scores, proportion=1):
        normalized_scores = {}
        score_sum = 0
        for _, score in scores.items():
            score_sum += score

        for idx in scores:
            normalized_scores[idx] = scores[idx] / score_sum * proportion

        return normalized_scores

    def module_contrib(self, ccgraph, dev_share):
        all_modules = {}

        for key, az in self._analyzers.items():
            all_modules.update(modules_contribution(az.graph, self.linguist[key]))

        aggregated_modules = get_aggregated_modules(all_modules)
        normalize_coef = sum(aggregated_modules.values())
        if normalize_coef == 0:
            normalize_coef = 1.0

        for email in dev_share.keys():
            dev_modules = {}
            for ccgraph in self._ccgraphs.values:
                dev_modules.update(modules_contribution(az.graph, self.linguist[key], email))

            dev_share[email]['modules'] = get_aggregated_modules_on_dev(aggregated_modules, dev_modules, normalize_coef)
        return dev_share

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

    def modules_contribution(ccgraph, proportion, email=None, alpha=0.85, black_set=[]):
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
                            modules_share[file] += dr/len(files)*1.0 * proportion
                        else:
                            modules_share[file] = dr/len(files)*1.0 * proportion

        return modules_share

    def developer_profile(self, pickle_path, alpha=0.85, show_merge=True):
        dev_share = {}

        commit_share = project_commit_share()

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

        dev_share = module_contrib(dev_share)

        return dev_share

##### Todo: process all private methods:
    def is_merged_commit(commit):
        if len(commit.parents) > 1:
            return True
        else:
            return False

    def save(self, fname):
        with open(fname, 'wb+') as f:
           pickle.dump(self, f)

    def basic_stats(self, pickle_path, alpha=0.85, show_merge=True):
        commit_share = project_commit_share()

        points = []
    

        for commit in self._ri.repo.iter_commits():

            if is_merged_commit(commit) and not show_merge:
                continue

            if commit.hexsha in commit_share:
                points.append(commit_share[commit.hexsha])
            else:
                points.append(0.0)

        return list(reversed(points))



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
