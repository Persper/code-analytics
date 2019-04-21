from abc import ABC, abstractclassmethod, abstractproperty
from typing import IO, Iterable
from aenum import IntFlag


class CommitInfo():
    """
    An immutable (git) commit information.
    """

    def __init__(self, hexsha: str = None, message: str = None, author_name: str = None, author_email: str = None):
        self._hexsha = hexsha
        self._message = message
        self._author_name = author_name
        self._author_email = author_email

    @property
    def hexsha(self):
        return self._hexsha

    @property
    def message(self):
        return self._message

    @property
    def author_name(self):
        return self._author_name

    @property
    def author_email(self):
        return self._author_email


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

    @abstractclassmethod
    def get_content_text(self, encoding: str = 'utf-8') -> str:
        return ""

    @abstractproperty
    def raw_content_stream(self) -> IO:
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
        return b""


class IRepositoryHistoryProvider(ABC):
    """
    Provides functionality for accessing commit history of a specified commit.
    """
    @abstractclassmethod
    def enum_commits(self, origin_commit_ref: str, terminal_commit_ref: str) -> Iterable[CommitInfo]:
        """
        Enumerates commits between the specified commit refs.
        params
            origin_commit_ref: commit ref from which to start enumeration. Use `None` to indicate the first commit.
            terminal_commit_ref: commit ref at which to end enumeration (inclusive). Use `master`/`HEAD` to indicate the latest commit.
        """
        pass


class IRepositoryWorkspaceFileFilter(ABC):
    """
    Provides functionality for filtering files and folders by their name and path in the workspace.
    """
    @abstractclassmethod
    def filter_file(self, file_name: str, file_path: str) -> bool:
        """
        Tests whether the specified file passes the filter.
        remarks
            The caller of this function does not guarantee the parent folder of the file passes the filter.
        """
        return False

    @abstractclassmethod
    def filter_folder(self, folder_name: str, folder_path) -> bool:
        """
        Tests whether the specified folder passes the filter.
        remarks
            This method is usually provided for pruning by folders during traversing.
        """
        return False


class IRepositoryWorkspaceProvider(ABC):
    """
    Provides functionality for accessing the workspace files and their diff of the specified commit ref.
    """
    @abstractclassmethod
    def get_commit_info(self, commit_ref: str) -> CommitInfo:
        pass

    @abstractclassmethod
    def get_files(self, commit_ref: str, filter: IRepositoryWorkspaceFileFilter = None) -> Iterable[IFileInfo]:
        pass

    def diff_between(self, base_commit_ref: str, current_commit_ref: str,
                     base_commit_filter: IRepositoryWorkspaceFileFilter = None,
                     current_commit_filter: IRepositoryWorkspaceFileFilter = None) -> Iterable[IFileDiff]:
        pass
