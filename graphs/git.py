from git.exc import InvalidGitRepositoryError, NoSuchPathError
from git import Repo
import sys

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