import logging
from typing import Callable, Collection, Dict, Iterable, NamedTuple, Tuple

import numpy as np
from numpy import linalg as LA
from scipy.sparse import coo_matrix

from persper.analytics2.abstractions.callcommitgraph import (
    Commit, Edge, IReadOnlyCallCommitGraph, Node, NodeHistoryItem,
    NodeHistoryLogicUnitItem, NodeId)

_logger = logging.getLogger(__name__)


class _NodeEntry(NamedTuple):
    index: int
    weight: float


class DevRankNodeResult(NamedTuple):
    weight: float
    devrank: float


def devrank(ccg: IReadOnlyCallCommitGraph, weight_func: Callable[[Node], float], alpha=0.85, epsilon=1e-5, max_iters=300) -> Dict[NodeId, DevRankNodeResult]:
    """Memory efficient DevRank using scipy.sparse

    Args:
               nodes - A sequence of nodes.
         weight_func - A function that provides weight of the specified `Node`.
               alpha - A float between 0 and 1, DevRank's damping factor.
             epsilon - A float.
           max_iters - An integer, specify max number of iterations to run.

    Returns:
        A dict with node names being keys and DevRanks being values.
    """
    node_info = {}
    # node ids
    ordered_nodes = []
    universe_size = 0
    row, col, data = [], [], []
    for i, node in enumerate(ccg.enum_nodes()):
        node: Node
        weight = weight_func(node)
        node_info[node.node_id] = _NodeEntry(i, weight)
        ordered_nodes.append(node.node_id)
        universe_size += weight
    num_nodes = len(ordered_nodes)

    p = np.empty(num_nodes)
    for node_index, node_id in enumerate(ordered_nodes):
        size_sum = 0
        to_ids = []
        # from callsite to defintion
        for e in ccg.enum_edges(from_name=node_id.name, from_language=node_id.language):
            e: Edge
            assert ccg.get_node(e.to_id)
            to_index, to_weight = node_info[e.to_id]
            size_sum += to_weight
            row.append(to_index)
            col.append(node_index)
            to_ids.append(e.to_id)
        for to_id in to_ids:
            data.append(node_info[to_id].weight / size_sum)
        cur_node_info = node_info[node_id]
        p[cur_node_info.index] = cur_node_info.weight / universe_size

    P = coo_matrix((data, (row, col)), shape=(num_nodes, num_nodes)).tocsr()

    v = np.ones(num_nodes) / num_nodes

    for i in range(max_iters):
        new_v = alpha * P.dot(v)
        gamma = LA.norm(v, 1) - LA.norm(new_v, 1)
        new_v += gamma * p
        delta = LA.norm(new_v - v, 1)
        if delta < epsilon:
            break
        v = new_v

    dr = {}
    for id in ordered_nodes:
        info = node_info[id]
        info: _NodeEntry
        dr[id] = DevRankNodeResult(info.weight, v[info.index])

    return dr


def create_history_weight_func(commits_black_list: Collection[str] = None):
    falled_back = None
    black_list_present = not not commits_black_list

    def weight_func(node: Node) -> int:
        nonlocal commits_black_list
        nonlocal falled_back
        nonlocal black_list_present
        if falled_back == None:
            if node.history_lu:
                falled_back = False
            elif node.history:
                _logger.warning("func_weight: Fell back to line-based commit history.")
                falled_back = True
            else:
                # history is empty
                return 1    # avoid DIV/0
        weight = 0
        if not falled_back:
            for h in node.history_lu:
                h: NodeHistoryLogicUnitItem
                if not black_list_present or h.hexsha not in commits_black_list:
                    weight += h.added_units + h.removed_units
        else:
            for h in node.history:
                h: NodeHistoryItem
                if not black_list_present or h.hexsha not in commits_black_list:
                    weight += h.added_lines + h.removed_lines
        # we need to take max between dev_eq and 1 to avoid zero division error
        return max(weight, 1)

    return weight_func


def create_history_weight_func_by_commit(commits_black_list: Collection[str] = None):
    falled_back = None
    black_list_present = not not commits_black_list

    def weight_func(node: Node) -> Dict[str, int]:
        nonlocal commits_black_list
        nonlocal falled_back
        nonlocal black_list_present
        if falled_back == None:
            if node.history_lu:
                falled_back = False
            elif node.history:
                _logger.warning("func_weight_by_commit: Fell back to line-based commit history.")
                falled_back = True
            else:
                # history is empty
                return 0
        result = {}
        if not falled_back:
            for h in node.history_lu:
                h: NodeHistoryLogicUnitItem
                if not black_list_present or h.hexsha not in commits_black_list:
                    result[h.hexsha] = result.get(h.hexsha, 0) + h.added_units + h.removed_units
        else:
            for h in node.history:
                h: NodeHistoryItem
                if not black_list_present or h.hexsha not in commits_black_list:
                    result[h.hexsha] = result.get(h.hexsha, 0) + h.added_lines + h.removed_lines
        return result

    return weight_func


def function_devranks(ccg: IReadOnlyCallCommitGraph, alpha, commits_black_list: Collection[str] = None):
    """
    Args:
            alpha - A float between 0 and 1, commonly set to 0.85
        black_set - A set of commit hexshas to be blacklisted

    Returns:
        A dict with keys being function IDs and values being devranks
    """
    return devrank(ccg, create_history_weight_func(commits_black_list), alpha=alpha)


def commit_function_devranks(ccg: IReadOnlyCallCommitGraph, alpha, commits_black_list: Collection[str] = None) -> Dict[str, Dict[str, float]]:
    """Show how a commit's devrank can be broken down into the partial devranks of the functions it changed
        Here is the formula for how much devrank commit c receives by changing function f:

            dr(c, f) = dr(f) * dev_eq(f, c) / dev_eq(f)

    Args:
            alpha - A float between 0 and 1, commonly set to 0.85
        black_set - A set of commit hexshas to be blacklisted

    Returns:
        A dict with keys being commit hexshas and values being dicts,
            whose values are function IDs and values are devranks

        Note: all commits are guaranteed to be present in the returned dict,
        even if they didn't touch any function (thus have an empty dict)
    """
    commit_function_devranks = {}

    for commit in ccg.enum_commits():
        commit: Commit
        commit_function_devranks[commit.hexsha] = {}

    func_devranks = function_devranks(ccg, alpha, commits_black_list)
    weight_by_commit = create_history_weight_func_by_commit(commits_black_list)

    for node in ccg.enum_nodes():
        node_id = node.node_id
        result: DevRankNodeResult = func_devranks[node_id]
        func_commits_dev_eq = weight_by_commit(node)
        # skip this node if empty (it's probably a built-in function or third-party dep)
        if len(func_commits_dev_eq) == 0:
            continue

        func_dev_eq = result.weight
        for hexsha, func_commit_dev_eq in func_commits_dev_eq.items():
            func_commit_dr = (func_commit_dev_eq / func_dev_eq) * result.devrank
            commit_function_devranks[hexsha][node_id] = func_commit_dr

    return commit_function_devranks


def commit_devranks(ccg: IReadOnlyCallCommitGraph, alpha, commits_black_list: Collection[str] = None):
    """Computes all commits' devranks from function-level devranks
        Here is the formula:

            dr(c) = sum(dr(c, f) for f in C_f)

        where dr(*) is the devrank function, dev_eq(*, *) is the development equivalent function,
        and C_f is the set of functions that commit c changed.

    Args:
            alpha - A float between 0 and 1, commonly set to 0.85
        black_set - A set of commit hexshas to be blacklisted

    Returns:
        A dict with keys being commit hexshas and values being commit devranks

            Note: all commits are guaranteed to be present in the returned dict,
            even if their devrank is 0 or they're present in the `black_set`
    """
    commit_devranks = {}
    commit_function_devranks_result = commit_function_devranks(ccg, alpha, commits_black_list)
    for hexsha, commit_dict in commit_function_devranks_result.items():
        commit_devranks[hexsha] = sum(commit_dict.values())
    return commit_devranks


def developer_devranks(ccg: IReadOnlyCallCommitGraph, alpha, commits_black_list: Collection[str] = None):
    """
    Args:
            alpha - A float between 0 and 1, commonly set to 0.85
        black_set - A set of commit hexshas to be blacklisted
    """
    developer_devranks = {}
    commit_devranks_result = commit_devranks(ccg, alpha, commits_black_list)

    for commit in ccg.enum_commits():
        commit: Commit
        if commit.hexsha not in commit_devranks_result:
            continue

        if commit.author_email in developer_devranks:
            developer_devranks[commit.author_email] += commit_devranks_result[commit.hexsha]
        else:
            developer_devranks[commit.author_email] = commit_devranks_result[commit.hexsha]
    return developer_devranks
