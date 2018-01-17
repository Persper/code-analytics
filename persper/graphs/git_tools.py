from git.exc import InvalidGitRepositoryError, NoSuchPathError
from git import Repo
import sys

EMPTY_TREE_SHA = '4b825dc642cb6eb9a060e54bf8d69288fbee4904'


def _diff_with_first_parent(commit):
    if len(commit.parents) == 0:
        prev_commit = EMPTY_TREE_SHA
    else:
        prev_commit = commit.parents[0]
    # commit.diff automatically detect renames
    return commit.diff(prev_commit,
                       create_patch=True, R=True, indent_heuristic=True)


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
    return repo.git.show('{}:{}'.format(commit.hexsha, path))
