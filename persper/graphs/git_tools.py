from git.exc import InvalidGitRepositoryError, NoSuchPathError
import git
import sys

def _diff_with_first_parent(commit):
    if len(commit.parents) == 0:
        prev_commit = git.NULL_TREE
    else:
        prev_commit = commit.parents[0]
    # commit.diff automatically detect renames
    return commit.diff(prev_commit,
                       create_patch=True, indent_heuristic=True)


def initialize_repo(repo_path):
    try:
        repo = git.Repo(repo_path)
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
