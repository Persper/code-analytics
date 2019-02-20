#!/usr/bin/env python
# -*- coding: utf-8 -*-

import os
import subprocess
import sys
import shutil
import networkx as nx

from git import Repo
from persper.util.path import root_path


def make_new_dir(dir_path):
    """delete old directory first if exists"""
    if os.path.exists(dir_path):
        shutil.rmtree(dir_path)
    os.makedirs(dir_path)


def remove_all_except_git(dir_path):
    for item in os.listdir(dir_path):
        # Do not delete the .git directory
        if item == ".git":
            continue
        path = os.path.join(dir_path, item)
        if os.path.isdir(path):
            shutil.rmtree(path)
        else:
            os.remove(path)


def copy_tree(src, dst, symlinks=False, ignore=None):
    """
    Copy all files/dirs under src to dst, a wrapper around shutil.copytree
    """
    for item in os.listdir(src):
        s = os.path.join(src, item)
        d = os.path.join(dst, item)
        if os.path.isdir(s):
            shutil.copytree(s, d, symlinks, ignore)
        else:
            shutil.copy2(s, d)


def find_first_commit(graph):
    first = None
    for n in graph.nodes():
        if graph.in_degree(n) == 0:
            if first is None:
                first = n
            else:
                print("Multiple starting nodes is not supported.")
                sys.exit()
    return first


def depth_first_traverse(graph, first_commit):
    stack = []
    visited = set()
    stack.append(first_commit)
    while len(stack) > 0:
        n = stack.pop()
        if n not in visited:
            sorted_out_nodes = sorted([x for x in graph[n]], reverse=True)
            stack += sorted_out_nodes
            visited.add(n)
            yield n


def simple_commit(repo, commit_dir, repo_path, commit_msg):
    """
    :param repo: a GitPython Repo object
    :param commit_dir: the dir which contains snapshot of target commit
    :param repo_path: path to target repo
    :param commit_msg:
    :return: the SHA of newly created commit
    """
    remove_all_except_git(repo_path)
    copy_tree(commit_dir, repo_path)
    repo.git.add("*")
    repo.git.commit("-m {}".format(commit_msg))
    sha = repo.git.rev_parse("HEAD")
    repo.git.tag(commit_msg)
    return sha


def find_the_other_parent(graph, node, parent):
    """
    Args:
        graph: networkx.Digraph, the commit graph
        node: a node in graph that has two parents
        parent: a node in graph, one of the two parents of the node

    Returns:
        A node in g, the other parent of n
    """
    for p in graph.pred[node]:
        if p != parent:
            return p


def create_repo(src_dir):
    """
    Assumes that merge only happens on master branch.
    """
    repo_name = os.path.basename(src_dir.rstrip('/'))
    repo_path = os.path.join(root_path, 'repos', repo_name)
    make_new_dir(repo_path)
    git_init_cmd = ['git', 'init', repo_path]
    subprocess.call(git_init_cmd)
    repo = Repo(repo_path)

    n_to_dir = {}
    for e in os.scandir(src_dir):
        n_to_dir[e.name] = e.path

    g = nx.DiGraph(
            nx.drawing.nx_pydot.read_dot(
                os.path.join(src_dir, 'cg.dot')
            )
        )

    first_commit = find_first_commit(g)

    last_n = None
    n_to_sha = {}
    additional_parents = {}
    for n in depth_first_traverse(g, first_commit):
        print(n)
        in_dg = g.in_degree(n)
        assert(in_dg in (0, 1, 2))

        # n is on the same branch as last_n
        if last_n is None or n in g[last_n]:
            sha = simple_commit(repo, n_to_dir[n], repo_path, n)
            n_to_sha[n] = sha

            # if n has 2 parents, then remember n and
            # add additional parent later
            if in_dg == 2:
                p = find_the_other_parent(g, n, last_n)
                additional_parents[p] = n

        # need to create a new branch for n
        else:
            assert(in_dg == 1)
            p = list(g.predecessors(n))[0]
            repo.git.checkout(n_to_sha[p])
            branch_name = "feature-" + n
            repo.git.checkout(b=branch_name)

            sha = simple_commit(repo, n_to_dir[n], repo_path, n)
            n_to_sha[n] = sha

        if n in additional_parents:
            second_parent = n
            child = additional_parents[n]
            first_parent = find_the_other_parent(g, child, second_parent)

            # add the second parent
            repo.git.replace(n_to_sha[child],
                             n_to_sha[first_parent],
                             n_to_sha[second_parent],
                             graft=True)

        # update last_n
        last_n = n

    repo.git.checkout('master')


def usage(cmd):
    print("Usage: {0} [src_dir]".format(cmd))
    print("\tCreate a git repository with fake development history.")
    print("\tEach subdirectory in src_dir contains the snapshot of a commit.")
    print(("\tThe depth first traversal will always visit the"
           "first node in alphabetical order"))


def main():
    if len(sys.argv) == 2:
        src_dir = sys.argv[1]
        create_repo(src_dir)
    else:
        usage(sys.argv[0])


if __name__ == "__main__":
    main()
