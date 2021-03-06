from abc import ABC, abstractmethod
from git import Commit, DiffIndex, Repo


class CommitClassifier(ABC):
    """
    Defines the interface of any commit classifier
    """

    @abstractmethod
    def predict(self, commit: Commit, diff_index: DiffIndex, repo: Repo):
        """
        Args:
            commit: A gitpython's Commit object.
            diff_index: A gitpython's DiffIndex object.
                It is a list of Diff object, each containing the
                diff information between a pair of old/new source files.
            repo: A gitpython's Repo object.


        Returns:
            A list, representing the probability distribution of each label
        """
        pass

    @property
    @abstractmethod
    def labels(self):
        """
        Returns:
            A list of label (str),
            in the same order as `predict` method's output.
        """
        pass
