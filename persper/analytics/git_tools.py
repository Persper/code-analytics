from git.exc import InvalidGitRepositoryError, NoSuchPathError
from git import Repo, Commit
from typing import Union
import sys
import git

EMPTY_TREE_SHA = '4b825dc642cb6eb9a060e54bf8d69288fbee4904'


def diff_with_first_parent(repo: Repo, commit: Commit):
    if len(commit.parents) == 0:
        return diff_with_commit(repo, commit, None)
    else:
        return diff_with_commit(repo, commit, commit.parents[0])


def diff_with_commit(repo: Repo, current_commit: Commit, base_commit_sha: str):
    if not base_commit_sha:
        base_commit = repo.tree(EMPTY_TREE_SHA)
    else:
        base_commit = repo.commit(base_commit_sha)
    return base_commit.diff(current_commit, create_patch=True, indent_heuristic=True)


def initialize_repo(repo_path):
    try:
        repo = Repo(repo_path)
    except InvalidGitRepositoryError as e:
        print("Invalid Git Repository!")
        sys.exit(-1)
    except NoSuchPathError as e:
        print("No such path error!")
        sys.exit(-1)
    return repo


def get_contents(repo, commit, path):
    """Get contents of a path within a specific commit"""
    if type(commit) == Commit:
        commit = commit.hexsha
    return repo.git.show('{}:{}'.format(commit, path))
