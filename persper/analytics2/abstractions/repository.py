from abc import ABC, abstractmethod, abstractproperty
from datetime import datetime
from typing import IO, Iterable, List, Union

from aenum import IntFlag


class IWorkspaceFileFilter(ABC):
    """
    Provides functionality for filtering files and folders by their name and path in the workspace.
    """
    @abstractmethod
    def filter_file(self, file_name: str, file_path: str) -> bool:
        """
        Tests whether the specified file passes the filter.
        remarks
            The caller of this function does not guarantee the parent folder of the file passes the filter.
        """
        return False

    @abstractmethod
    def filter_folder(self, folder_name: str, folder_path) -> bool:
        """
        Tests whether the specified folder passes the filter.
        remarks
            This method is usually provided for pruning by folders during traversing.
        """
        return False


class IFileInfo(ABC):
    """
    Provides functionality for accessing a specific file in the repository.
    """
    @abstractproperty
    def name(self) -> str:
        """
        Gets the local name without path of the file.
        """
        return ""

    @abstractproperty
    def path(self) -> str:
        """
        Gets the full repo-relative path of the file.
        """
        return ""

    @abstractproperty
    def size(self) -> int:
        """
        Gets the length of the file.
        """
        return -1

    @abstractproperty
    def raw_content(self) -> bytes:
        return b""

    @abstractmethod
    def get_content_text(self, encoding: str = 'utf-8') -> str:
        return ""

    @abstractproperty
    def raw_content_stream(self) -> IO:
        pass


class ICommitInfo(ABC):
    """
    A commit information.
    """

    @abstractproperty
    def hexsha(self) -> str:
        return ""

    @abstractproperty
    def message(self) -> str:
        return ""

    @abstractproperty
    def author_name(self) -> str:
        return ""

    @abstractproperty
    def author_email(self) -> str:
        return ""

    @abstractproperty
    def authored_time(self) -> datetime:
        return datetime(2000, 1, 1)

    @abstractproperty
    def committer_name(self) -> str:
        return ""

    @abstractproperty
    def committer_email(self) -> str:
        return ""

    @abstractproperty
    def committed_time(self) -> datetime:
        return datetime(2000, 1, 1)

    @abstractproperty
    def parents(self) -> List["ICommitInfo"]:
        """
        Gets the parent commits of the current commit.
        """
        return None

    @abstractmethod
    def enum_files(self, filter: IWorkspaceFileFilter = None) -> Iterable["IFileInfo"]:
        """
        Enumerates all the files in the current commit.
        """
        pass

    @abstractmethod
    def diff_from(self, base_commit_ref: Union[str, "ICommitInfo"],
                  current_commit_filter: IWorkspaceFileFilter = None,
                  base_commit_filter: IWorkspaceFileFilter = None) -> Iterable["IFileDiff"]:
        """
        Compares the current commit to the specified commit.
        params
            base_commit_ref: Base commit ref or `ICommitInfo` to perform diff from. Use `None` for empty tree.
            current_commit_filter: Used to filter workspace files of current commit.
            base_commit_filter: Used to filter workspace files of base commit.
        remarks
            If a file has been renamed and/or it cannot pass either one of `current_commit_filter` and `base_commit_filter`,
            the returned `IFileDiff` will be as if the file does not exists in current commit or base commit.
        """
        pass


class FileDiffOperation(IntFlag):
    _init_ = "value __doc__"
    Unchanged = 0, "File not changed in the aspects covered by this enum. Still, file attributes might be changed."
    Modified = 1, "File content has been changed."
    Renamed = 2, "File name has been changed."
    Added = 4, "File has been added to the workspace."
    Deleted = 8, "File has been deleted from workspace."


class IFileDiff(ABC):
    """
    Provides functionality for accessing the content diff of a specific file in the repository.
    """
    @abstractproperty
    def old_file(self) -> IFileInfo:
        """
        File information before change. `None` if the old file does not exist.
        """
        pass

    @abstractproperty
    def new_file(self) -> IFileInfo:
        """
        File information after change. `None` if the new file does not exist (deleted).
        """
        pass

    @abstractproperty
    def operation(self) -> FileDiffOperation:
        return FileDiffOperation.Unchanged

    @abstractproperty
    def patch(self) -> bytes:
        """
        Gets the (git) patch between old file and new file content.
        remarks
            This property might be unapplicable in certain situation,
            (e.g. the old file / new file has been filtered out, while the other one filtered in)
            in which case an Exception can be thrown.
        """
        return b""


class IRepositoryHistoryProvider(ABC):
    """
    Provides functionality for accessing commit history of a specified commit.
    """
    @abstractmethod
    def get_commit_info(self, commit_ref: str) -> ICommitInfo:
        pass

    @abstractmethod
    def enum_commits(self, origin_commit_ref: str, terminal_commit_ref: str) -> Iterable[ICommitInfo]:
        """
        Enumerates commits between the specified commit refs.
        params
            origin_commit_ref: commit ref from which to start enumeration. Use `None` to indicate the first commit.
            terminal_commit_ref: commit ref at which to end enumeration (inclusive). Use "master"/"HEAD" to indicate the latest commit.
        remarks
            The commits should be enumerated by topological order, i.e., the parents of a commit should already been enumerated,
            as long as they are in the range of `origin_commit_ref..terminal_commit_ref`.
        """
        pass
