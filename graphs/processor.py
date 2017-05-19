import time
from graphs.git import initialize_repo
import functools
print = functools.partial(print, flush=True)

EMPTY_TREE_SHA = '4b825dc642cb6eb9a060e54bf8d69288fbee4904'

def _diff_with_first_parent(commit):
    if len(commit.parents) == 0: 
        prev_commit = EMPTY_TREE_SHA
    else:
        prev_commit = commit.parents[0]
    # commit.diff automatically detect renames
    return commit.diff(prev_commit, create_patch=True, R=True)

def _fill_change_type(diff_index):
    for diff in diff_index:
        if diff.new_file:
            diff.change_type = 'A'
        elif diff.deleted_file:
            diff.change_type = 'D'
        elif diff.renamed: 
            diff.change_type = 'R'
        elif (diff.a_blob and diff.b_blob and 
             (diff.a_blob != diff.b_blob)):
            diff.change_type = 'M'
        else:
            diff.change_type = 'U'

def _print_diff_index(diff_index):
    print(" ".join([diff.change_type for diff in diff_index]))

def _subject(msg):
    return msg.split('\n', 1)[0].lstrip().rstrip() 

class Processor():

    def __init__(self, repo_path):
        self.repo_path = repo_path
        self.repo = initialize_repo(repo_path)
        self.git = self.repo.git

    def process(self, from_beginning=False, num_commits=None, rev=None, 
        into_branches=False, verbose=False, max_branch_length=100):
        """
        This function supports two ways of specifying the
        range of commits to process: 

        Method 1: Set from_beginning to True and 
            pass num_commits parameter. Using this
            method, the function will start from the
            very first commit on the master branch and
            process the following num_commits commits
            (also on the master branch).

        Method 2: Set from_beginning to False and
            pass rev parameter. rev is the revision
            parameter which follows an extended SHA-1 syntax.
            Please refer to git-rev-parse for viable options.
            rev should only include commits on the master branch.

        Args:
            rev: A string, see above.
            num_commits: An int, see above.
            from_beginning: A boolean flag, see above.
            into_branches: A boolean flag, if True, the process function
                will operate in two phases. 

                In the first phase, a call commit graph is contructed 
                by traversing the specified range of commits on the master 
                branch. Merge commits are detected and recorded if the 
                start commit (on master) and end/merge commit of the 
                corresponding branch are both within the range of
                traversal. Those recorded merge commits do not 
                get any credits (thus they are not present in 
                self.history data structure).

                In the second phase, it traverses all the branches detected
                in the first phase and assign them due credits.   

            max_branch_length: An int, the maximum number of commits
                to trace back before abortion.
        """
        if from_beginning:
            if num_commits == None:
                num_commits = 0
            self.commits = list(
                self.repo.iter_commits(first_parent=True))[-num_commits:]
        else:
            self.commits = list(self.repo.iter_commits(
                rev, max_count=num_commits, first_parent=True))

        self._reset_state()

        counter = 1
        start = time.time()

        # 1st phase
        for commit in reversed(self.commits):
            sha = commit.hexsha
            self.visited.add(sha)
            self._start_process_commit(commit)

            if verbose:
                print('------ No.{} {} {} ------'.format(
                    counter, sha, _subject(commit.message)))
            else:
                print('------ No.{} {} ------'.format(counter, sha))
            if counter % 100 == 0:
                print('------ Used time: {} ------'.format(
                    time.time() - start))

            # generate diff_index by diff commit with its first parent
            diff_index = _diff_with_first_parent(commit)

            # figure out the change type of each entry in diff_index
            _fill_change_type(diff_index)

            if verbose:
                _print_diff_index(diff_index)

            if into_branches:
                is_merge_commit = self._detect_branch(commit, max_branch_length)
            else: 
                is_merge_commit = False

            for diff in diff_index:
                if diff.change_type == 'U':
                    print('Unknown change type encountered.')
                    continue

                if diff.change_type == 'A':
                    self.on_add(diff, commit, is_merge_commit) 

                elif diff.change_type == 'D':
                    self.on_delete(diff, commit, is_merge_commit)

                elif diff.change_type == 'R':
                    self.on_rename(diff, commit, is_merge_commit)

                else:
                    self.on_modify(diff, commit, is_merge_commit)

            counter += 1


        # 2nd phase
        if into_branches:

            counter = 1 
            branch_cnt = 1
            start = time.time()

            print('\n-------  2nd phase -------\n')
            for branch in self.branches:
                for commit in branch:
                    self._start_process_commit(commit)

                    if verbose:
                        print('------ Commit No.{} '.format(counter),
                              'Branch No.{} {} {}------'.format(
                                branch_cnt, commit.hexsha, _subject(commit.message)))
                    else:
                        print('------ Commit No.{} '.format(counter),
                              'Branch No.{} {}------'.format(
                                branch_cnt, commit.hexsha))
                    if counter % 100 == 0:
                        print('------ Used time: {} ------'.format(
                            time.time() - start))

                    # generate diff_index by diff commit with its first parent
                    diff_index = _diff_with_first_parent(commit)

                    # figure out the change type of each entry in diff_index
                    _fill_change_type(diff_index)

                    if verbose:
                        _print_diff_index(diff_index)

                    for diff in diff_index:
                        if diff.change_type == 'U':
                            print('Unknown change type encountered.')
                            continue

                        if diff.change_type == 'A':
                            self.on_add2(diff, commit) 

                        elif diff.change_type == 'D':
                            self.on_delete2(diff, commit)

                        elif diff.change_type == 'R':
                            self.on_rename2(diff, commit)

                        else:
                            self.on_modify2(diff, commit)

                    counter += 1
                branch_cnt += 1

    def _reset_state(self):
        self.visited = set()
        self.branches = []

    def _start_process_commit(self, commit):
        pass

    def on_add(self, diff, commit, is_merge_commit):
        return 0 

    def on_delete(self, diff, commit, is_merge_commit):
        return 0 

    def on_rename(self, diff, commit, is_merge_commit):
        return 0 

    def on_modify(self, diff, commit, is_merge_commit):
        return 0 

    def on_add2(self, diff, commit):
        return 0 

    def on_delete2(self, diff, commit):
        return 0 

    def on_rename2(self, diff, commit):
        return 0 

    def on_modify2(self, diff, commit):
        return 0 

    def _detect_branch(self, commit, max_branch_length):
        found = False
        if len(commit.parents) == 2:
            branch_length = 1
            cur_commit = commit.parents[1]
            branch = [cur_commit]

            while(branch_length <= max_branch_length):
                prev_commit = cur_commit.parents[0]  
                if (prev_commit.hexsha in self.visited or 
                    len(prev_commit.parents) == 0):
                    found = True
                    break
                branch.append(prev_commit)
                cur_commit = prev_commit
                branch_length += 1

            if found:
                self.branches.append(list(reversed(branch)))
        return found


