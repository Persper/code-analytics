import os
import time
import pickle
from graphs.git_tools import initialize_repo
from collections import deque
import functools
print = functools.partial(print, flush=True)

EMPTY_TREE_SHA = '4b825dc642cb6eb9a060e54bf8d69288fbee4904'


def _diff_with_first_parent(commit):
    if len(commit.parents) == 0:
        prev_commit = EMPTY_TREE_SHA
    else:
        prev_commit = commit.parents[0]
    # commit.diff automatically detect renames
    return commit.diff(prev_commit,
                       create_patch=True, R=True, indent_heuristic=True)


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
        self.visited = set()
        self.last_processed_commit = None

    def process(self, rev=None,
                from_beginning=False, num_commits=None,
                from_last_processed=False, end_commit_sha=None,
                into_branches=False,
                max_branch_length=100,
                min_branch_date=None,
                checkpoint_interval=100,
                skip_work=False,
                verbose=True):
        """
        This function supports four ways of specifying the
        range of commits to process:

        Method 1: rev
            Pass `rev` parameter and set both
            `from_beginning` and `from_last_processed` to False.
            `rev` is the revision specifier which follows
            an extended SHA-1 syntax. Please refer to git-rev-parse
            for viable options. `rev' should only include commits
            on the master branch.

        Method 2: from_beginning & num_commits (optional)
            Set `from_beginning` to True and
            pass `num_commits` parameter. Using this
            method, the function will start from the
            very first commit on the master branch and
            process the following `num_commits` commits
            (also on the master branch).

        Method 3: from_last_processed & num_commits
            Set `from_last_processed` to True and pass
            `num_commits` parameter. Using this method, the
            function will resume processing from succeeding commit of
            `self.last_processed_commit` for `num_commits` commits.

        Method 4: from_last_processed & end_commit_sha
            Set `from_last_processed` to True and pass
            `end_commit_sha` parameter. The range of continued processing
            will be `self.last_processed_commit.hexsha..end_commit_sha`.

        Args:
            rev: A string, see above.
            num_commits: An int, see above.
            from_beginning: A boolean flag, see above.
            from_last_processed: A boolean flag, see above.
            end_commit_sha: A string, see above.
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
            min_branch_date: A python time object, stop backtracing if
                a commit is authored before this time.
            checkpoint_interval: An int.
        """
        if not from_last_processed:
            self._reset_state()
        self.merge_commits = deque()

        # Method 2
        if from_beginning:
            if num_commits is None:
                num_commits = 0
            self.commits = list(
                self.repo.iter_commits(first_parent=True))[-num_commits:]

        elif from_last_processed:
            if not self.last_processed_commit:
                print("No history exists yet, terminated.")
                return

            # Method 4
            if end_commit_sha:
                rev = self.last_processed_commit.hexsha + '..' + end_commit_sha
                self.commits = list(self.repo.iter_commits(
                    rev, first_parent=True))
            # Method 3
            elif num_commits:
                rev = self.last_processed_commit.hexsha + '..master'
                self.commits = list(self.repo.iter_commits(
                    rev, first_parent=True))[-num_commits:]
            else:
                print("Both end_commit_sha and num_commits are None.")
                return

        else:
            # Method 1
            self.commits = list(self.repo.iter_commits(rev, first_parent=True))

        if len(self.commits) > 0:
            self.last_processed_commit = self.commits[0]
        else:
            print("The range specified is empty, terminated.")
            return

        counter = 1
        start = time.time()

        # 1st phase
        for commit in reversed(self.commits):
            sha = commit.hexsha
            self.visited.add(sha)
            self._start_process_commit(commit)

            if verbose:
                print('------ No.{} {} {} {} ------'.format(
                    counter, sha, _subject(commit.message),
                    time.strftime(
                        "%b %d %Y", time.gmtime(commit.authored_date)
                    ))
                )
            else:
                print('------ No.{} {} ------'.format(counter, sha))
            if counter % 100 == 0:
                print('------ Used time: {} ------'.format(
                    time.time() - start))

            if counter % checkpoint_interval == 0:
                repo_name = os.path.basename(self.repo_path.rstrip('/'))
                self.save(repo_name + '-1st-' + str(counter) + '.pickle')

            if into_branches:
                is_merge_commit = len(commit.parents) > 1
                if is_merge_commit:
                    self.merge_commits.append(commit)
                """
                is_merge_commit = self._detect_branch(
                    commit, max_branch_length, min_branch_date)
                """
            else:
                is_merge_commit = False

            if not skip_work:
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

            commit_cnt = 1
            branch_cnt = 1
            start = time.time()

            print('\n-------  2nd phase -------\n')

            while len(self.merge_commits) > 0:
                mc = self.merge_commits.popleft()
                cur_commit = mc.parents[1]
                branch_length = 0
                valid_branch = False

                while True:

                    # stop tracing back along this branch
                    # if cur_commit has been visited
                    if cur_commit.hexsha in self.visited:
                        break

                    # stop if we have reached time boundary
                    authored_date = time.gmtime(cur_commit.authored_date)
                    if min_branch_date and min_branch_date > authored_date:
                        break

                    # stop if we have reached max_branch_length
                    if branch_length >= max_branch_length:
                        break

                    # stop if we have reached the very first commit
                    if len(cur_commit.parents) == 0:
                        break

                    # will process at least one commit for this branch
                    valid_branch = True

                    # process this commit
                    if verbose:
                        print('------ Commit No.{} '.format(commit_cnt),
                              'Branch No.{} {} {} {} ------'.format(
                                branch_cnt,
                                cur_commit.hexsha,
                                _subject(cur_commit.message),
                                time.strftime(
                                    "%b %d %Y",
                                    time.gmtime(cur_commit.authored_date)
                                )
                            )
                        )
                    else:
                        print('------ Commit No.{} '.format(commit_cnt),
                              'Branch No.{} {}------'.format(
                                branch_cnt, cur_commit.hexsha))

                    if commit_cnt % 100 == 0:
                        print('------ Used time: {} ------'.format(
                            time.time() - start))

                    if commit_cnt % checkpoint_interval == 0:
                        repo_name = os.path.basename(
                            self.repo_path.rstrip('/'))
                        self.save(
                            repo_name + '-2nd-' + str(counter) + '.pickle')

                    self.visited.add(cur_commit.hexsha)
                    # add to queue if prev_commit is a merge commit
                    if len(cur_commit.parents) == 2:
                        self.merge_commits.append(cur_commit)

                    if not skip_work:
                        self._start_process_commit(cur_commit)
                        diff_index = _diff_with_first_parent(cur_commit)
                        _fill_change_type(diff_index)
                        for diff in diff_index:
                            if diff.change_type == 'U':
                                print('Unknown change type encountered.')
                                continue
                            if diff.change_type == 'A':
                                self.on_add2(diff, cur_commit)
                            elif diff.change_type == 'D':
                                self.on_delete2(diff, cur_commit)
                            elif diff.change_type == 'R':
                                self.on_rename2(diff, cur_commit)
                            else:
                                self.on_modify2(diff, cur_commit)

                    # get next commit
                    prev_commit = cur_commit.parents[0]

                    cur_commit = prev_commit
                    branch_length += 1
                    commit_cnt += 1

                if valid_branch:
                    branch_cnt += 1

        repo_name = os.path.basename(self.repo_path.rstrip('/'))
        self.save(repo_name + '-finished.pickle')

    def _reset_state(self):
        self.visited = set()
        self.last_processed_commit = None

    def _start_process_commit(self, commit):
        pass

    def set_repo_path(self, repo_path):
        self.repo_path = repo_path
        self.repo = initialize_repo(repo_path)
        self.last_processed_commit = self.repo.commit(self.last_sha)

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

    def __getstate__(self):
        state = {
            'visited': self.visited,
            'last_sha': self.last_processed_commit.hexsha
        }
        return state

    def __setstate__(self, state):
        self.__dict__.update(state)

    def save(self, fname):
        with open(fname, 'wb+') as f:
            pickle.dump(self, f)
