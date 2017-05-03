import time
from graphs.git import initialize_repo
import functools
print = functools.partial(print, flush=True)

class Processor():

    EMPTY_TREE_SHA = '4b825dc642cb6eb9a060e54bf8d69288fbee4904'

    def __init__(self, repo_path):
        self.repo_path = repo_path
        self.repo = initialize_repo(repo_path)
        self.git = self.repo.git

    def process(self, rev=None, num_commits=None, 
                from_beginning=False, verbose=False):
        if from_beginning:
            if num_commits == None:
                num_commits = 0
            self.commits = list(
                self.repo.iter_commits(first_parent=True))[-num_commits:]
        else:
            self.commits = list(self.repo.iter_commits(
                rev, max_count=num_commits, first_parent=True))

        self.start_process()

        counter = 1
        start = time.time()
        for commit in reversed(self.commits):
            sha = commit.hexsha
            self.start_process_commit(commit)

            print('------ No.{} {} ------'.format(counter, sha))
            if counter % 100 == 0:
                print('------ Used time: {} ------'.format(time.time() - start))

            if not commit.parents:
                diff_index = commit.diff(Processor.EMPTY_TREE_SHA, 
                    create_patch=True, R=True)
            else:
                last_commit = commit.parents[0]
                diff_index = commit.diff(last_commit,
                    create_patch=True, R=True)

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
                    print("Unknown change type encountered.")
                    continue

            if verbose:
                print('{}:{}'.format(sha, " ".join([diff.change_type for diff in diff_index])))

            for diff in diff_index:
                if diff.change_type == 'U':
                    continue

                if diff.change_type == 'A':
                    self.on_add(diff, commit) 

                elif diff.change_type == 'D':
                    self.on_delete(diff, commit)

                elif diff.change_type == 'R':
                    self.on_rename(diff, commit)

                else:
                    self.on_modify(diff, commit)

            self.finish_process_commit(commit)
            counter += 1

        self.finish_process()

    def start_process(self):
        pass

    def finish_process(self):
        pass

    def start_process_commit(self, commit):
        pass

    def finish_process_commit(self, commit):
        pass

    def on_add(self, diff, commit):
        return 0 

    def on_delete(self, diff, commit):
        return 0 

    def on_rename(self, diff, commit):
        return 0 

    def on_modify(self, diff, commit):
        return 0 

        


