from git.exc import InvalidGitRepositoryError, NoSuchPathError
from git import Repo, Commit
from typing import Union
import sys
import git
import codecs

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
    return base_commit.diff(current_commit, create_patch=True, indent_heuristic=True,
                            ignore_blank_lines=True, ignore_space_change=True)


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
    byte_str = repo.git.show('{}:{}'.format(commit, path), stdout_as_string=False)
    # default utf-8
    encoding = 'utf-8'
    # the following code is from: https://github.com/chardet/chardet/blob/master/chardet/universaldetector.py#L137
    # encoding names are from here: https://docs.python.org/3/library/codecs.html
    if byte_str.startswith(codecs.BOM_UTF8):
        # EF BB BF  UTF-8 with BOM
        encoding = 'utf-8-sig'
    elif byte_str.startswith(codecs.BOM_UTF32_LE):
        # FF FE 00 00  UTF-32, little-endian BOM
        encoding = 'utf-32-le'
    elif byte_str.startswith(codecs.BOM_UTF32_BE):
        # 00 00 FE FF  UTF-32, big-endian BOM
        encoding = 'utf-32-be'
    elif byte_str.startswith(codecs.BOM_LE):
        # FF FE  UTF-16, little endian BOM
        encoding = 'utf-16-le'
    elif byte_str.startswith(codecs.BOM_BE):
        # FE FF  UTF-16, big endian BOM
        encoding = 'utf-16-be'
    return byte_str.decode(encoding=encoding, errors='replace')
