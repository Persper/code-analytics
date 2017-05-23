from enum import Enum
import argparse
import networkx as nx
import sys
import os
import subprocess
from graphs.parse_patch import parse_patch
from graphs.cpp_tools import get_func_ranges_cpp, fname_filter_cpp
from graphs.ruby_tools import get_func_ranges_ruby, fname_filter_ruby
from graphs.git_tools import initialize_repo, get_contents
from graphs.processor import Processor
from graphs.write_graph_to_dot import write_G_to_dot_with_pr

parser = argparse.ArgumentParser(
    description="Draw commit graph for a git repository")
parser.add_argument('repo', type=str, 
    help="path to target repo")
parser.add_argument('language', type=str, 
    help="programming language of the target repo, currently support [cpp, ruby]")
parser.add_argument('--output', type=str, 
    help="output path of generated svg, default as working directory")

class Language(Enum):
    CPP = 1
    RUBY = 2

def add_edge(G, sp, ep, func_id):
    if ep in G[sp]:
        G[sp][ep]['func_ids'].append(func_id)
    else:
        G.add_edge(sp, ep, func_ids=[func_id])
        
def intersected(a, b):
    return a[0] <= b[0] <= a[1] or b[0] <= a[0] <= b[1]

def get_modified_func_ids(func_ranges, modified_intervals, func_ids):
    search_ptr = 0
    num_intervals = len(modified_intervals)
    modified_func_ids = []
    for func_r, func_id in zip(func_ranges, func_ids):
        for i in range(search_ptr, num_intervals):
            if intersected(func_r, modified_intervals[i]):
                
                modified_func_ids.append(func_id)
                search_ptr = i
                break
    return modified_func_ids

class CommitGraph(Processor):

    def __init__(self, repo_path, language_str):
        super().__init__(repo_path)
        language = Language[language_str]
        if language == Language.CPP:
            self.fname_filter = fname_filter_cpp
            self.func_extractor = get_func_ranges_cpp
        elif language == Language.RUBY:
            self.fname_filter = fname_filter_ruby
            self.func_extractor = get_func_ranges_ruby
        else:
            print("This language is not supported yet!")

    def start_process(self):
        self.G = nx.DiGraph()
        self.func_commit = {}

    def start_process_commit(self, commit):
        self.G.add_node(commit.hexsha)

    def on_add(self, diff, commit):
        fname = diff.b_blob.path
        sha = commit.hexsha
        if self.fname_filter(fname):
            file_contents = get_contents(self.repo, commit, fname)
            func_ids, _ = self.func_extractor(file_contents, fname)
            for func_id in func_ids:
                self.func_commit[func_id] = sha

    def on_delete(self, diff, commit):
        fname = diff.a_blob.path
        sha = commit.hexsha
        if self.fname_filter(fname):
            last_commit = commit.parents[0]
            file_contents = get_contents(self.repo, last_commit, fname)
            func_ids, _ = self.func_extractor(file_contents, fname)
            for func_id in func_ids:
                if func_id in self.func_commit:
                    add_edge(self.G, sha, self.func_commit[func_id], func_id)
                    del self.func_commit[func_id]

    def on_rename(self, diff, commit):
        # when similarity is 100%, diff.a_blob and diff.b_blob are None, so don't use them
        new_fname = diff.rename_to
        old_fname = diff.rename_from
        last_commit = commit.parents[0]
        sha = commit.hexsha

        if self.fname_filter(new_fname) or self.fname_filter(old_fname):
            file_contents = get_contents(self.repo, last_commit, old_fname)
            func_ids, func_ranges = self.func_extractor(file_contents, old_fname)
            try:
                modified_intervals = parse_patch(diff.diff.decode("utf-8"))
            except UnicodeDecodeError:
                print("UnicodeDecodeError Found in change_type {}".format(diff.change_type))
                return -1
            modified_func_ids = get_modified_func_ids(func_ranges, modified_intervals, func_ids)
            for func_id in modified_func_ids:
                if func_id in self.func_commit:
                    add_edge(self.G, sha, self.func_commit[func_id], func_id)
                self.func_commit[func_id] = sha 

    def on_modify(self, diff, commit):
        assert diff.b_blob.path == diff.a_blob.path
        fname = diff.b_blob.path
        last_commit = commit.parents[0]
        sha = commit.hexsha

        if self.fname_filter(fname):
            file_contents = get_contents(self.repo, last_commit, fname)
            func_ids, func_ranges = self.func_extractor(file_contents, fname)
            try:
                modified_intervals = parse_patch(diff.diff.decode("utf-8"))
            except UnicodeDecodeError:
                print("UnicodeDecodeError Found in change_type {}".format(diff.change_type))
                return -1
            modified_func_ids = get_modified_func_ids(func_ranges, modified_intervals, func_ids)
            
            for func_id in modified_func_ids:
                if func_id in self.func_commit:
                    add_edge(self.G, sha, self.func_commit[func_id], func_id)
                self.func_commit[func_id] = sha


def draw_commit_graph(repo_path, language, output_path=None, num_commits=None):
    repo_name = os.path.basename(repo_path)
    cg = CommitGraph(repo_path, language)
    cg.process(from_beginning=True, num_commits=num_commits)
    pr = nx.pagerank(cg.G, alpha=0.85)
    write_G_to_dot_with_pr(cg.G, pr, repo_name + ".dot", edge_attrib="func_ids")
    subprocess.call('dot -Tsvg {}.dot -o {}.svg'.format(repo_name, repo_name), shell=True)

def main():
    args = parser.parse_args()
    draw_commit_graph(args['repo'], args['language']) 

if __name__ == '__main__':
    main()
