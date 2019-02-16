from persper.analytics.cpp import CPPGraphServer
from persper.analytics.analyzer import Analyzer
from persper.analytics.graph_server import CPP_FILENAME_REGEXES

ALPHA = 0.85


def build_analyzer(repo_url, pickle_path, repo_path):
    az = Analyzer(repo_path, CPPGraphServer(CPP_FILENAME_REGEXES))
    az.analyze(repo_url, pickle_path, from_beginning=True, into_branches=True)
    return pickle_path

def developer_profile(pickle_path, alpha=0.85, show_merge=True):
    dev_share = {}
    az = pickle.load(open(pickle_path, 'rb'))

    commit_share = az.get_graph().commit_devranks(alpha, black_set)

    for commit in az._ri.repo.iter_commits():

        if is_merged_commit(commit) and not show_merge:
            continue

        email = commit.author.email

        if email in dev_share:
            # dev_share[email]["share"] += commit_share
            dev_share[email]["commits"].appned(commit)
        else:
            dev_share[email] = {}
            dev_share[email]["commits"] = [commit]
            dev_share[email]["email"] = email
            # dev_share[email]["share"] = commit_share

    for dev, values in dev_share:
        init_commit, last_commit, values = share_distribution(values['commits'], commit_share)
        values['distribution'] = {
            'init_commit': init_commit,
            'last_commit': last_commit
            'values': values
        }
        values['dev_value'] = sum(values)

    return dev_share

def share_distribution(commits, commit_share):
    shares = {}
    for commit in commits:
        if commit.hexsha in commit_share:
            if commit.authored_date in shares:
                shares[commit.authored_date] += commit_share[commit.hexsha]
            else:
                shares[commit.authored_date] = commit_share[commit.hexsha]

    shares = dict(sorted(shares.items()))

    init_commit = share[0].key
    last_commit = share[-1].key

    values = []
    for date in interval(init_commit, last_commit):
        if shares[date]:
            values.appned(shares[date])
        else:
            values.appned(0)

    return init_commit, last_commit, values