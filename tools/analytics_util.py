import pickle
import itertools
import numpy as np
import pandas as pd
import matplotlib.pyplot as plt
from sklearn import svm
from scipy import stats
from github import Github
from datetime import date, datetime, timedelta
from sklearn.model_selection import train_test_split

alpha = 0.85

black_set = [
    # Below two commits are auto-fix commits, so we 
    # will not consider them during the analysis.
    '8bd66202c324a6c7a79abc0f1f0558dacbc59460',
    '0a61b0df1224a5470bcddab302bc199ca5a9e356'
]


def merged_pr(user_name, password, repo='bitcoin/bitcoin'):
    """
    Args:
        user_name: The user name used to login the GitHub,
            usually showed as the suffixe of your homepage link.
        password: Github password.
        repo: Full name of a project in GitHub,
            including the owner name and project name
    Returns:
        The number of merged PR and closed PR for the given
        repo.
    """
    merged_number = 0
    closed_pr_number = 0
    g = Github(user_name, password)
    repo = g.get_repo(repo)
    pulls = repo.get_pulls(state='closed', base='master')

    for pr in pulls:
        closed_pr_number += 1
        if pr.merged_at != None:
            merged_number += 1

    return merged_number, closed_pr_number


def accumulated_share_and_commit(az, alpha=0.85, show_merge=False):
    """
    Args:
        az: The analyzer instance
        show_merge: a indicator to show if we want to include the
            merge commits in the response.
    Returns:
        Accumulated shares and commits
    """
    commit_share = az.get_graph().commit_devranks(alpha, black_set)
    shares = {}
    commits = {}
    for commit in az._ri.repo.iter_commits():
        if commit.hexsha in commit_share:
            if is_merged_commit(commit) and not show_merge:
                continue

            if commit.authored_date in shares:
                shares[commit.authored_date] += commit_share[commit.hexsha]
                commits[commit.authored_date] += 1
            else:
                shares[commit.authored_date] = commit_share[commit.hexsha]
                commits[commit.authored_date] = 1

    # Sort shares and commits according to commit authored_date
    shares = dict(sorted(shares.items()))
    commits = dict(sorted(commits.items()))

    # Calculate the accumulated value of both shares and commits
    commit_sum = 0
    share_sum = 0
    for key, val in shares.items():
        share_sum += val
        commit_sum += commits[key]
        shares[key] = share_sum
        commits[key] = commit_sum

    # accumulated shares and commits
    return shares, commits


# The function to plot the curve for accumulated shares and commits
def plot_accumulated_share_and_commit(path, show_merge=False):
    az = pickle.load(open(path, 'rb'))
    shares, commits = accumulated_share_and_commit(az, 0.85, show_merge)

    share_dates = [datetime.fromtimestamp(ts) for ts in list(shares.keys())]
    share_values = list(shares.values())

    commit_dates = [datetime.fromtimestamp(ts) for ts in list(commits.keys())]
    commit_values = list(commits.values())

    # Plot share value curve
    fig, ax1 = plt.subplots()
    plt.xticks(rotation=25)
    ax1.set_xlabel('Time')
    ax1.set_ylabel('Share Value')
    ax1.plot(share_dates, share_values)

    # Plot commit curve
    # ax2 = ax1.twinx()
    # ax2.set_ylabel('# Commits')
    # ax2.plot(commit_dates, commit_values, 'r', label='commits')

    return plt


# Reference: https://stackoverflow.com/questions/304256/whats-the-best-way-to-find-the-inverse-of-datetime-isocalendar
def iso_year_start(iso_year):
    "The gregorian calendar date of the first day of the given ISO year"
    fourth_jan = date(iso_year, 1, 4)
    delta = timedelta(fourth_jan.isoweekday() - 1)
    return fourth_jan - delta


def iso_to_gregorian(iso_year, iso_week, iso_day):
    "Gregorian calendar date for the given ISO year, week and day"
    year_start = iso_year_start(iso_year)
    return year_start + timedelta(days=iso_day - 1, weeks=iso_week - 1)


def commit_with_date(az, alpha=0.85, show_merge=False):
    commits = []
    commit_share = az.get_graph().commit_devranks(alpha, black_set)

    for sha in commit_share:
        if is_merged_commit(az._ri.repo.commit(sha)) and not show_merge:
            continue

        email = az._ri.repo.commit(sha).author.email
        authored_date = datetime.fromtimestamp(az._ri.repo.commit(sha).authored_date)

        commits.append({
            "email": email,
            "sha": sha,
            "share": commit_share[sha],
            "date": authored_date,
            "year": authored_date.year,
            "month": authored_date.month,
            "week": authored_date.year * 100 + authored_date.isocalendar()[1]})

    return pd.DataFrame(commits)


def plt_commits_share_againest_week(df):
    groups = df.groupby("week").groups
    dates = []
    shares = []
    commits = []
    weeks = []
    for k in groups.keys():
        group_df = df.iloc[groups[k].tolist()]
        weeks.append(k)
        dates.append(iso_to_gregorian(group_df.year.iloc[0], k % 100, 1))
        shares.append(group_df.share.values.sum())
        commits.append(len(group_df))

    fig, ax1 = plt.subplots()
    plt.xticks(rotation=25)
    ax1.set_xlabel('Time')
    ax1.set_ylabel('Share Value')
    ax1.plot(dates, shares)

    # Plot commit curve
    ax2 = ax1.twinx()
    ax2.set_ylabel('# Commits')
    ax2.plot(dates, commits, color='r', label='commits')

    df_in_week = pd.DataFrame(list(zip(dates, shares, commits, weeks)),
                              columns=['date', 'share', 'commit_number', 'week'])
    return plt, df_in_week


def plt_commits_share_againest_month(df):
    groups = df.groupby(["year", 'month']).groups
    dates = []
    shares = []
    commits = []
    for k in groups.keys():
        dates.append(date(int(k[0]), int(k[1]), 1))
        shares.append(df.iloc[groups[k].tolist()].share.values.sum())
        commits.append(len(groups[k]))

    fig, ax1 = plt.subplots()
    plt.xticks(rotation=25)
    ax1.set_xlabel('Time')
    ax1.set_ylabel('Share Value')
    ax1.plot(dates, shares)

    # Plot commit curve
    ax2 = ax1.twinx()
    ax2.set_ylabel('# Commits')
    ax2.plot(dates, commits, color='r', label='commits')

    return plt


def plt_commits_share_againest_year(df):
    groups = df.groupby(["year"]).groups
    dates = []
    shares = []
    commits = []
    for k in groups.keys():
        dates.append(date(int(k), 1, 1))
        shares.append(df.iloc[groups[k].tolist()].share.values.sum())
        commits.append(len(groups[k]))

    fig, ax1 = plt.subplots()
    plt.xticks(rotation=25)
    ax1.set_xlabel('Time')
    ax1.set_ylabel('Share Value')
    ax1.plot(dates, shares)

    # Plot commit curve
    ax2 = ax1.twinx()
    ax2.set_ylabel('# Commits')
    ax2.plot(dates, commits, color='r', label='commits')

    return plt


def accumulated_data_for_dev(az, email, show_merge=False):
    share = az._graph_server.get_graph().commit_devranks(0.85, black_set)
    init_commit = '4405b78d6059e536c36974088a8ed4d9f0f29898'
    share_in_date = {}
    commit_in_date = {}
    if email == 's_nakamoto@1a98c847-1fd6-4fd8-948a-caf3550aa51b':
        share_in_date[az._ri.repo.commit(init_commit).authored_date] = share[init_commit]
        commit_in_date[az._ri.repo.commit(init_commit).authored_date] = 1

    for commit in az._ri.repo.iter_commits():

        if commit.hexsha == '4405b78d6059e536c36974088a8ed4d9f0f29898':
            continue

        if str(commit.hexsha) in share and (commit.author.email == email or commit.author.email=='satoshin@gmx.com'):

            if is_merged_commit(commit) and not show_merge:
                continue

            if commit.authored_date in share_in_date:
                share_in_date[commit.authored_date] += share[str(commit.hexsha)]
                commit_in_date[commit.authored_date] += 1
            else:
                share_in_date[commit.authored_date] = share[str(commit.hexsha)]
                commit_in_date[commit.authored_date] = 1
    share_in_date = dict(sorted(share_in_date.items()))
    commit_in_date = dict(sorted(commit_in_date.items()))

    commit_sum = 0
    share_sum = 0

    for key, val in share_in_date.items():
        share_sum += val
        commit_sum += commit_in_date[key]
        share_in_date[key] = share_sum
        commit_in_date[key] = commit_sum

    return share_in_date, commit_in_date


def plot_share_and_commit_for_dev(path, email, show_merge=False):
    az = pickle.load(open(path, 'rb'))
    shares, commits = accumulated_data_for_dev(az, email, show_merge)

    share_dates = [datetime.fromtimestamp(ts) for ts in list(shares.keys())]
    share_values = list(shares.values())

    # commit_dates = [datetime.fromtimestamp(ts) for ts in list(commits.keys())]
    # commit_values = list(commits.values())

    # Plot share value curve
    fig, ax1 = plt.subplots()
    plt.xticks(rotation=25)
    ax1.set_xlabel('Time')
    ax1.set_ylabel('Share Value')
    ax1.plot(share_dates, share_values)

    return plt


def developer_profile(az, alpha=0.85, show_merge=False):
    dev_share = {}
    share = az.get_graph().commit_devranks(alpha, black_set)
    loc = az.get_graph().locrank_commits()
    loc = dict(loc)

    for commit in az._ri.repo.iter_commits():
        if is_merged_commit(commit) and not show_merge:
            continue

        commit_share = share[commit.hexsha] if commit.hexsha in share else 0
        commit_loc = loc[commit.hexsha] if commit.hexsha in loc else 0
        email = commit.author.email
        commit_insertions = commit.stats.total['insertions']
        commit_deletions = commit.stats.total['deletions']

        if commit.hexsha == '4405b78d6059e536c36974088a8ed4d9f0f29898':
            email = 's_nakamoto@1a98c847-1fd6-4fd8-948a-caf3550aa51b'

        if email in dev_share:
            dev_share[email]["share"] += commit_share
            dev_share[email]["loc"] += commit_loc
            dev_share[email]["commit"] += 1
            dev_share[email]["insertion"] += commit_insertions
            dev_share[email]["deletion"] += commit_deletions

        else:
            dev_share[email] = {}
            dev_share[email]["commit"] = 1
            dev_share[email]["email"] = email
            dev_share[email]["share"] = commit_share
            dev_share[email]["loc"] = commit_loc
            dev_share[email]["insertion"] = commit_insertions
            dev_share[email]["deletion"] = commit_deletions

    return dev_share


def l2r(X, y):
    X_train, X_test, y_train, y_test = train_test_split(
        X, y, test_size=0.2, random_state=42)

    # data_scaler = StandardScaler().fit(X_train)
    # X_train = data_scaler.transform(X_train)

    comb = itertools.combinations(range(X_train.shape[0]), 2)
    k = 0
    Xp, yp, diff = [], [], []
    for (i, j) in comb:
        Xp.append(X_train[i] - X_train[j])
        diff.append(y_train[i] - y_train[j])
        yp.append(np.sign(diff[-1]))
        # output balanced classes
        if yp[-1] != (-1) ** k:
            yp[-1] *= -1
            Xp[-1] *= -1
            diff[-1] *= -1
        k += 1
    Xp, yp, diff = map(np.asanyarray, (Xp, yp, diff))
    clf = svm.LinearSVC(random_state=42, max_iter=4000)
    clf.fit(Xp, yp)
    coef = clf.coef_.ravel() / np.linalg.norm(clf.coef_)

    tau_train, _ = stats.kendalltau((np.dot(X_train, coef)), y_train)
    tau_test, _ = stats.kendalltau((np.dot(X_test, coef)), y_test)

    return tau_train, tau_test, clf


def is_merged_commit(commit):
    if len(commit.parents) > 1:
        return True
    else:
        return False
