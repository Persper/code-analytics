import time
from persper.graphs.git_tools import initialize_repo
from collections import deque


class RepoIterator():

    def __init__(self, repo_path):
        self.repo_path = repo_path
        self.repo = initialize_repo(repo_path)
        self.visited = set()
        self.last_processed_commit = None

    def iter(self, rev=None,
             from_beginning=False,
             num_commits=None,
             continue_iter=False,
             end_commit_sha=None,
             into_branches=False,
             max_branch_length=100,
             min_branch_date=None):
        """
        This function supports four ways of specifying the
        range of commits to return:

        Method 1: rev
            Pass `rev` parameter and set both
            `from_beginning` and `continue_iter` to False.
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

        Method 3: continue_iter & num_commits
            Set `continue_iter` to True and pass
            `num_commits` parameter. Using this method, the
            function will resume processing from succeeding commit of
            `self.last_processed_commit` for `num_commits` commits.

        Method 4: continue_iter & end_commit_sha
            Set `continue_iter` to True and pass
            `end_commit_sha` parameter. The range of continued processing
            will be `self.last_processed_commit.hexsha..end_commit_sha`.

        Args:
            rev: A string, see above.
            num_commits: An int, see above.
            from_beginning: A boolean flag, see above.
            continue_iter: A boolean flag, see above.
            end_commit_sha: A string, see above.
            into_branches: A boolean flag, if True, the iter function
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
        commits = None
        branch_commits = None

        if not continue_iter:
            self._reset_state()

        # Method 2
        if from_beginning:
            commits = list(self.repo.iter_commits(first_parent=True))
            if num_commits is not None:
                commits = commits[-num_commits:]

        elif continue_iter:
            if not self.last_processed_commit:
                print("No history exists yet, terminated.")
                return [], []

            # Method 4
            if end_commit_sha:
                rev = self.last_processed_commit.hexsha + '..' + end_commit_sha
                commits = list(self.repo.iter_commits(
                    rev, first_parent=True))
            # Method 3
            elif num_commits:
                rev = self.last_processed_commit.hexsha + '..master'
                commits = list(self.repo.iter_commits(
                    rev, first_parent=True))[-num_commits:]
            else:
                print("Both end_commit_sha and num_commits are None.")
                return [], []

        else:
            # Method 1
            commits = list(self.repo.iter_commits(rev, first_parent=True))

        # set self.last_processed_commit
        if len(commits) > 0:
            self.last_processed_commit = commits[0]
        else:
            print("The range specified is empty, terminated.")
            return [], []

        for commit in reversed(commits):
            self.visited.add(commit.hexsha)

        if into_branches:
            # find all merge commits
            start_points = deque()
            for commit in reversed(commits):
                if len(commit.parents) > 1:
                    for pc in commit.parents[1:]:
                        start_points.append(pc)

            branch_commits = []

            while len(start_points) > 0:
                cur_commit = start_points.popleft()
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
                        print("WARNING: MAX_BRANCH_LENGTH reached.")
                        break

                    self.visited.add(cur_commit.hexsha)
                    branch_commits.append(cur_commit)
                    branch_length += 1

                    # stop if we have reached the very first commit
                    if len(cur_commit.parents) == 0:
                        break

                    # add to queue if cur_commit is a merge commit
                    if len(cur_commit.parents) > 1:
                        for pc in cur_commit.parents[1:]:
                            start_points.append(pc)

                    # get next commit
                    prev_commit = cur_commit.parents[0]
                    cur_commit = prev_commit

        return commits, branch_commits

    def _reset_state(self):
        self.visited = set()
        self.last_processed_commit = None
