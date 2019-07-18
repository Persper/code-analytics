from persper.analytics.git_tools import diff_with_commit
from persper.util.cache import Cache
from git import Commit, DiffIndex, Repo
from typing import Optional, Union

"""diff_index cache key namespace"""
DIFF_INDEX_NS = 'diff_index'


def cached_diff_with_commit(repo: Repo, commit: Union[Commit, str], parentCommit: Union[Commit, str],
                            cache: Optional[Cache] = None) -> DiffIndex:
    if cache is not None:
        cache_key = ':'.join([DIFF_INDEX_NS,
                              get_hexsha_from_commit(commit),
                              get_hexsha_from_commit(parentCommit)])

        diff_index = cache.get(cache_key, serializer='pickle')
        if diff_index is not None:
            return diff_index
        else:
            diff_index = diff_with_commit(repo, commit, parentCommit)
            if diff_index is not None:
                cache.put(cache_key, diff_index, serializer='pickle')
    else:
        diff_index = diff_with_commit(repo, commit, parentCommit)
    return diff_index


def get_hexsha_from_commit(commit: Union[Commit, str]) -> str:
    if commit is None:
        return 'none_commit'
    elif type(commit) is str:
        return commit
    else:
        return commit.hexsha
