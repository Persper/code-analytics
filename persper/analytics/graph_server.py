from abc import ABC
from abc import abstractmethod
from aenum import Enum
from persper.analytics.call_commit_graph import CallCommitGraph

JS_FILENAME_REGEXES = [
    r'.+\.js$',
    r'^(?!dist/).+',
    r'^(?!test(s)?/).+',
    r'^(?!spec/).+',
    r'^(?!build/).+',
    r'^(?!bin/).+',
    r'^(?!doc(s)?/).+'
]

# todo(hezheng) consider moving these regexes to their corresponding language file
C_FILENAME_REGEXES = [
    r'.+\.(h|c)$'
]

# http://gcc.gnu.org/onlinedocs/gcc-4.4.1/gcc/Overall-Options.html#index-file-name-suffix-71
CPP_FILENAME_REGEXES = {
    r'.+\.(c|cc|cxx|cpp|CPP|c\+\+|C|hh|hpp|Hpp|h\+\+|H)$'
}

GO_FILENAME_REGEXES = [
    r'.+\.go$'
]

JAVA_FILENAME_REGEXES = [
    r'.+\.java$'
]


class CommitSeekingMode(Enum):
    """
    Describes how `Analyzer` has reached the current commit. 
    """
    _init_ = "value __doc__"
    NormalForward = 0, """
    The current commit has been reached because `Analyzer` is going to analyze this commit.
    `GraphServer` implementation should update its working tree according to the subsequent
    `update_graph` calls, as well as the call commit graph preserved inside `GraphServer`.
    """
    MergeCommit = 1, """
    The current commit has been reached because `Analyzer` is going to analyze this commit.
    However, the current commit is a merge commit. Some commit graph traits might be
    updated differently from NormalForward case; for example, we still update edges,
    but we don't update node history in this commit.
    """
    Rewind = 2, """
    The current commit has been reached because `Analyzer` is tracing back (or more generally, "jumping")
    to the parent commit (A^) of certain commit (A). Usually there should be no changes to the commit graph
    preserved in the GraphServer during going through the diff of this commit. But yet GraphServer should update
    its workspace tree accordingly, because the next commit shall be the "certain commit" (A) to be analyzed
    either as `NormalForward` or `MergeCommit`.
    To ensure GraphServer can correctly obtain the file change information, Analyzer
    will go to its parent commit (A^) first
    """


class GraphServer(ABC):
    r"""
    Provides implementation-specific ability to build call commit graph via
    some or all of the commits in a repository.

    `analyzer2.Analyzer` is the consumer of this class. It will ensure the methods be called
    in the following order:

    ```
    lastCommit = EMPTY_TREE_SHA
    for commit in commits: 
        start_commit(commit)
        for oldFileName, fileName, fileDiff in compareCommit(lastCommit, commit):
            filter_file(oldFileName)
            filter_file(fileName)
            update_graph(oldFileName, fileName, fileDiff)
        end_commit(commit)
        lastCommit = commit
    ```

    `Analyzer` will visit a range of commits in certain order (though it's usually
    topology order because we may reduce as more Rewinds as possible), and it will
    indicate how it has reached the current commit in `start_commit`. Because the
    commit history is not linear, we may sometimes need to move backwards (rewind)
    in the commit tree. In that case, we need to ensure `GraphServer` can always
    get the correct file diff from __parent__ commit. For example, in a commit tree
    like this
    ```
    A -- B -- C -- D -- E -- F
         \ -- a -- b -- /
    ```
    where `master` == `F`, `Analyzer` may visit the commits in the following order
    * A (NormalForward)
    * B (NormalForward)
    * C (NormalForward)
    * D (NormalForward)
    * B (Rewind)
    * a (NormalForward)
    * b (NormalForward)
    * E (MergeCommit)
    * F (NormalForward)

    When implementing this class, you should ensure to
    * Update both the edge (call relation) and node history for `NormalForward` commits
    * Update edge but keep node history untouched for `MergeCommit` commits
    * Do not update call commit graph for `Rewind` commits

    The existence of `Rewind` commits is only to simplify the node history generation
    for `GraphServer`, because node history means the diff to the __parent__ commit.

    If there is any Error raised in any of the implementation methods, the status of
    `GraphSever` will be unspecified. It's suggested the consumer of `GraphServer`
    create a new instance of it.

    When overriding this class, some of the methods may be implemented either as
    synchronous or asynchronous (with `asyncio`, or `async def`). You will find the
    note on the methods respectively.
    """

    def register_commit(self, hexsha, author_name, author_email,
                        commit_message):
        """
        Deprecated. Do not override this method.
        Override start_commit instead.
        :return: a status code, success or failure
        """
        raise NotImplementedError()

    @abstractmethod
    def update_graph(self, old_filename: str, old_src: str,
                     new_filename: str, new_src: str, patch: bytes):
        """
        Notifies `GraphServer` a file has been changed in this commit.
        params
            :param old_filename: the path to a file that the commit modifies
            :param old_src: the source code of the file before the commit
            :param new_filename: the path to the file after the commit
            :param new_src: the source code of the file after the commit
            :param patch: the raw patch generated by GitPython diff
        
        remarks
            This method can be implemented as async method.
            The name of this function is kept for backward-compatibility.
            It's up to implementation to decide whether to update the
            call commit graph on the fly, or to only make necessary work
            tree modifications in this method, and update the call commit
            graph in whole in `end_commit` method. You may also choose to
            update some part of the graph in `update_graph`, and the rest
            in `end_commit`.
        """
        pass

    def start_commit(self, hexsha: str, seeking_mode: CommitSeekingMode, author_name: str,
                     author_email: str, commit_message: str):
        """
        Called when the `Analyzer` has reached a new commit.
        params
            hexsha          hex SHA of the commit.
            seeking_mode    describes how this commit has been reached.
                            See CommitSeekingMode for more details on the meaning of each value.
            commit_message  commit summary.

        remarks
            When implementing this method, you might want to preserve `seeking_mode` as a class field
            so you may have access to this value in `update_graph` & `end_commit` implementations.
        """
        # default implementation for backwards compatibility
        if seeking_mode == CommitSeekingMode.NormalForward:
            self.register_commit(hexsha, author_name, author_email, commit_message)

    def end_commit(self, hexsha: str):
        """
        Called when the `Analyzer` is going to leave this commit.

        remarks
            This method can be implemented as async method.
        """
        pass

    @abstractmethod
    def get_graph(self) -> CallCommitGraph:
        """
        Retrieve the graph
        :return: A CallCommitGraph object
        """
        pass

    @abstractmethod
    def reset_graph(self):
        """Reset the graph discarding all data"""
        pass

    @abstractmethod
    def filter_file(self, filename):
        """
        Check if the file should be filtered out
        :param filename: the path of the file to check
        :return: True if the file should be selected; False otherwise.
        """
        pass

    @abstractmethod
    def config(self, param: dict):
        """
        One-time configuration of the server for following calls
        :param param: key-value pairs of configuration
        """
        pass
