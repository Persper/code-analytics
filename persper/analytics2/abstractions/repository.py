from abc import ABC, abstractclassmethod, abstractproperty
from typing import IO, Iterable


class CommitInfo():
    """
    An immutable (git) commit information.
    """
    def __init__(self, hexsha: str = None, comment: str = None, author_name: str = None, author_email: str = None):
        self._hexsha = hexsha
        self._comment = comment
        self._author_name = author_name
        self._author_email = author_email

    @property
    def hexsha(self):
        return self._hexsha

    @property
    def comment(self):
        return self._comment

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
    def patch(self) -> bytes:
        return b""


class IRepositoryHistoryProvider(ABC):
    @abstractclassmethod
    def enum_commits(self, origin_commit_ref: str, terminal_commit_ref: str) -> Iterable[CommitInfo]:
        pass


class IRepositoryWorkspaceProvider(ABC):
    @abstractclassmethod
    def get_commit_info(self, commit_ref: str) -> CommitInfo:
        pass

    @abstractclassmethod
    def get_files(self, commit_ref: str) -> Iterable[IFileInfo]:
        pass

    def diff_between(self, base_commit_ref: str, current_commit_ref: str) -> Iterable[IFileDiff]:
        pass
