from persper.analytics.git_tools import diff_with_commit

"""diff_index cache key namespace"""
DIFF_INDEX_NS = 'diff_index'


def cached_diff_with_commit(repo, commit, parentCommit, cache=None):
    if cache is not None:
        cache_key = ':'.join([DIFF_INDEX_NS,
                              _get_hexsha_from_commit(commit),
                              _get_hexsha_from_commit(parentCommit)])

        diff_index = cache.get(cache_key)
        if diff_index is not None:
            return diff_index
        else:
            diff_index = diff_with_commit(repo, commit, parentCommit)
            if diff_index is not None:
                cache.put(cache_key, diff_index)
    else:
        diff_index = diff_with_commit(repo, commit, parentCommit)
    return diff_index


def _get_hexsha_from_commit(commit):
    if commit is None:
        return 'none_commit'
    elif type(commit) is str:
        return commit
    else:
        return commit.hexsha
