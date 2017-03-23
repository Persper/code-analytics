from enum import Enum
import argparse
import networkx as nx
from git import Repo
from parse_patch import parse_patch
from cpp_tools import get_func_ranges_cpp, fname_filter_cpp
from ruby_tools import get_func_ranges_ruby, fname_filter_ruby

EMPTY_TREE_SHA = "4b825dc642cb6eb9a060e54bf8d69288fbee4904"

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
        
def get_contents(repo, commit, path):
    """Get contents of a path within a specific commit"""
    return repo.git.show('{}:{}'.format(commit.hexsha, path))

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

def build_function_level_commit_graph(repo, fname_filter, 
    func_extractor, num_commits=None, verbose=True):
    """Construct function-level commit graph for given repo
    Args:
        repo: a Repo object of gitpython
        fname_filter: a boolean function which takes filename as input,
            skip the input file if fname_filter evaluates to False
        func_extractor: a function for extracting functions within src file,
            takes two input, first is the contents of that src file,
            and second is the filename of the src file
        num_commits: an integer specifying the first number of commits to look at 
        verbose: a boolean indicator, if set to True, change type information of
            each commit would be printed
        
    Returns:
        A nx.Digraph object containing the commit graph
    """
    if not num_commits:
        num_commits = 0
    commits = list(repo.iter_commits())[-num_commits:]
    G = nx.DiGraph()
    fc_to_ct = {}
    for commit in reversed(commits):
        # add commit to graph as a new node
        sha = commit.hexsha
        G.add_node(sha)
    
        if not commit.parents:
            diff_index = commit.diff(EMPTY_TREE_SHA, create_patch=True, R=True)
        else:
            # parents[0] is the commit that was merged into
            last_commit = commit.parents[0]
            diff_index = commit.diff(last_commit, create_patch=True, R=True)
            
        # workaround a GitPython bug when create_patch is set to True 
        # change_type "R100", see link below for details 
        # https://github.com/gitpython-developers/GitPython/issues/563
        for diff in diff_index:
            if diff.new_file:
                diff.change_type = 'A'
            elif diff.deleted_file:
                diff.change_type = 'D'
            elif diff.renamed: 
                diff.change_type = 'R'
            elif diff.a_blob and diff.b_blob and diff.a_blob != diff.b_blob:
                diff.change_type = 'M'
            else:
                diff.change_type = 'U'
                print("Take a look at this commit!!! {}".format(sha))
                # raise Exception('Non-existent Change Type!')
                continue
            
        # iterate over changes
        if verbose:
            print("{}: {}".format(sha, " ".join([diff.change_type for diff in diff_index])))
        for diff in diff_index:
            if diff.change_type == 'U':
                continue
            if diff.change_type == 'A':
                fname = diff.b_blob.path
                if fname_filter(fname):
                    file_contents = get_contents(repo, commit, fname)
                    func_ids, _ = func_extractor(file_contents, fname)
                    for func_id in func_ids:
                        fc_to_ct[func_id] = sha
            elif diff.change_type == 'D':
                fname = diff.a_blob.path
                if fname_filter(fname):
                    file_contents = get_contents(repo, last_commit, fname)
                    func_ids, _ = func_extractor(file_contents, fname)
                    for func_id in func_ids:
                        if func_id in fc_to_ct:
                            add_edge(G, sha, fc_to_ct[func_id], func_id)
                            del fc_to_ct[func_id]
            elif diff.change_type == 'R':
                # when similarity is 100%, diff.a_blob and diff.b_blob are None, so don't use them
                new_fname = diff.rename_to
                old_fname = diff.rename_from
                if fname_filter(new_fname) or fname_filter(old_fname):
                    file_contents = get_contents(repo, last_commit, old_fname)
                    func_ids, func_ranges = func_extractor(file_contents, old_fname)
                    try:
                        modified_intervals = parse_patch(diff.diff.decode("utf-8"))
                    except UnicodeDecodeError:
                        print("UnicodeDecodeError Found in change_type {}".format(diff.change_type))
                        continue
                    modified_func_ids = get_modified_func_ids(func_ranges, modified_intervals, func_ids)
                    for func_id in modified_func_ids:
                        if func_id in fc_to_ct:
                            add_edge(G, sha, fc_to_ct[func_id], func_id)
                        fc_to_ct[func_id] = sha
            else:
                # change_type 'M'
                assert diff.b_blob.path == diff.a_blob.path
                fname = diff.b_blob.path
                if fname_filter(fname):
                    file_contents = get_contents(repo, commit, fname)
                    func_ids, func_ranges = func_extractor(file_contents, fname)
                    try:
                        modified_intervals = parse_patch(diff.diff.decode("utf-8"))
                    except UnicodeDecodeError:
                        print("UnicodeDecodeError Found in change_type {}".format(diff.change_type))
                        continue
                    modified_func_ids = get_modified_func_ids(func_ranges, modified_intervals, func_ids)
                    
                    for func_id in modified_func_ids:
                        if func_id in fc_to_ct:
                            add_edge(G, sha, fc_to_ct[func_id], func_id)
                        fc_to_ct[func_id] = sha
                        
    return G

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

def draw_commit_graph(repo_path, language, output_path=None, num_commits=None):
    repo = initialize_repo(repo_path)

    repo_name = os.path.basename(repo_path)

    if language == Language.CPP:
        G = build_function_level_commit_graph(repo, fname_filter_cpp, 
                                            get_func_ranges_cpp, num_commits=num_commits)
    elif language == Language.RUBY:
        G = build_function_level_commit_graph(repo, fname_filter_ruby, 
                                            get_func_ranges_ruby, num_commits=num_commits)
    else:
        print("This language is not supported yet!")
        sys.exit(-1)

    pr = nx.pagerank(G, alpha=0.85)
    write_G_to_dot_with_pr(G, pr, repo_name + ".dot", edge_attrib="func_ids")
    subprocess.call('dot -Tsvg {}.dot -o {}.svg'.format(repo_name, repo_name), shell=True)

def main():
    args = parser.parse_args()
    
    draw_commit_graph(args['repo'], Language[args['language']], ) 

if __name__ == '__main__':
    main()
