#!/usr/bin/env python
# -*- coding: utf-8 -*-

import os
import subprocess
import sys
import shutil
import networkx as nx

from git import Repo
from util.path import root_path

def make_new_dir(dir_path):
	"""delete old directory first if exists"""
	if os.path.exists(dir_path):
		shutil.rmtree(dir_path)	
	os.makedirs(dir_path)

def delete_files_under_dir(dir_path):
	for e in os.scandir(dir_path):
		if e.is_file():
			os.remove(e.path)

def copy_files(src_dir_path, dest_dir_path):
	for e in os.scandir(src_dir_path):
		if e.is_file():
			shutil.copyfile(e.path, os.path.join(dest_dir_path, e.name))

def find_first_commit(G):
	fcn = None
	for n in G.nodes_iter():
		if G.in_degree(n) == 0:
			if fcn == None:
				fcn = n
			else:
				print("Multiple starting nodes is not supported.")
				sys.exit()
	return fcn

def depth_first_traverse(G, fcn):
	stack = []
	visited = set()
	stack.append(fcn)
	while len(stack) > 0:
		n = stack.pop()
		if n not in visited:
			sorted_out_nodes = sorted([x for x in G[n]], reverse=True)
			stack += sorted_out_nodes
			visited.add(n)
			yield n

def simple_commit(repo, commit_dir, repo_path, commit_msg):
	"""
	Args:
		commit_dir: the dir which contains shapshot of target commit
		repo_path: path to target repo

	Returns:
		the SHA of newly created commit
	"""
	delete_files_under_dir(repo_path)
	copy_files(commit_dir, repo_path)
	repo.git.add("*")
	repo.git.commit("-m {}".format(commit_msg))
	sha = repo.git.rev_parse("HEAD")
	return sha

def find_the_other_parent(G, n, p):
	"""
	Args:
		G: networkx.Digraph, the commit graph
		n: A node in G that has two parents
		p: A node in G, one of the two parents of n

	Returns: 
		A node in G, the other parent of n
	"""
	for np in G.pred[n]:
		if np != p:
			return np

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

	G = nx.DiGraph(
			nx.drawing.nx_pydot.read_dot(
				os.path.join(src_dir, 'cg.dot')
			)
		)

	fcn = find_first_commit(G)

	last_n = None
	n_to_sha = {}
	additional_parents = {}
	for n in depth_first_traverse(G, fcn):
		print(n)
		in_dg = G.in_degree(n)
		assert(in_dg in (0, 1, 2))

		# n is on the same branch as last_n 
		if last_n == None or n in G[last_n]:
			sha = simple_commit(repo, n_to_dir[n], repo_path, n)
			n_to_sha[n] = sha

			# if n has 2 parents, then remember n and
			# add additional parent later	
			if in_dg == 2:
				p = find_the_other_parent(G, n, last_n)
				additional_parents[p] = n

		# need to create a new branch for n	
		else:
			assert(in_dg == 1)
			p = G.predecessors(n)[0]
			repo.git.checkout(n_to_sha[p])
			branch_name = "feature-" + n 
			repo.git.checkout(b=branch_name)

			sha = simple_commit(repo, n_to_dir[n], repo_path, n)
			n_to_sha[n] = sha

		if n in additional_parents:
			second_parent = n
			child = additional_parents[n]
			first_parent = find_the_other_parent(G, child, second_parent)

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

