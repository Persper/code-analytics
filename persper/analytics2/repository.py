import logging
from io import TextIOWrapper
from time import monotonic

from git import Blob, Commit, Diff, DiffIndex, Repo

from .abstractions.repository import (CommitInfo, FileDiffOperation, IFileDiff,
                                      IFileInfo, IRepositoryHistoryProvider,
                                      IRepositoryWorkspaceFileFilter,
                                      IRepositoryWorkspaceProvider)

_logger = logging.getLogger(__name__)

EMPTY_TREE_SHA = '4b825dc642cb6eb9a060e54bf8d69288fbee4904'


class GitRepository(IRepositoryHistoryProvider, IRepositoryWorkspaceProvider):
    def __init__(self, repo_path: str, first_parent_only: bool = False):
        self._repo = Repo(repo_path)
        self._first_parent_only = first_parent_only

    @staticmethod
    def _commit_info_from_commit(commit: Commit):
        return CommitInfo(commit.hexsha, commit.message, commit.author.name, commit.author.email)

    @staticmethod
    def _diff_with_commit(repo: Repo, current_commit: str, base_commit_sha: str):
        if not base_commit_sha:
            base_commit = repo.tree(EMPTY_TREE_SHA)
        else:
            base_commit = repo.commit(base_commit_sha)
        return base_commit.diff(current_commit, create_patch=True, indent_heuristic=True,
                                ignore_blank_lines=True, ignore_space_change=True)

    def enum_commits(self, origin_commit_ref: str, terminal_commit_ref: str):
        if not terminal_commit_ref:
            raise ValueError(
                "terminal_commit_ref should not be None or empty.")
        commitSpec = self._repo.rev_parse(terminal_commit_ref).hexsha
        if origin_commit_ref:
            commitSpec = commitSpec + ".." + \
                self._repo.rev_parse(terminal_commit_ref).hexsha
        _logger.debug("enum_commits starts on %s, first_parent=%s",
                      commitSpec, self._first_parent_only)
        for commit in self._repo.iter_commits(commitSpec, topo_order=True, reverse=True, first_parent=self._first_parent_only):
            yield GitRepository._commit_info_from_commit(commit)
        _logger.debug("enum_commits finishes on %s", commitSpec)

    def get_commit_info(self, commit_ref: str):
        commit = self._repo.rev_parse(commit_ref)
        return GitRepository._commit_info_from_commit(commit)

    def get_files(self, commit_ref: str, filter: IRepositoryWorkspaceFileFilter = None):
        commit = self._repo.rev_parse(commit_ref)

        def filterPred(i: Blob, d):
            return i.type == "blob"

        def prunePred(i: Blob, d):
            if i.type == "tree":
                return filter and not filter.filter_folder(i.name, i.path)
            elif i.type == "blob":
                return filter and not filter.filter_file(i.name, i.path)
            return False
        blobs = commit.tree.traverse() if not filter else commit.tree.traverse(
            filterPred, prunePred)
        for blob in blobs:
            yield GitFileInfo(blob)

    def diff_between(self, base_commit_ref: str, current_commit_ref: str,
                     base_commit_filter: IRepositoryWorkspaceFileFilter = None,
                     current_commit_filter: IRepositoryWorkspaceFileFilter = None):
        t0 = monotonic()
        diff_index = GitRepository._diff_with_commit(
            self._repo, current_commit_ref, base_commit_ref)
        _logger.debug("diff_between %s and %s used %.2fs.",
                      base_commit_ref, current_commit_ref, monotonic() - t0)
        for diff in diff_index:
            hide_base_file = base_commit_filter and diff.a_blob and not base_commit_filter.filter_file(
                diff.a_blob.name, diff.a_blob.path)
            hide_current_file = current_commit_filter and diff.b_blob and not current_commit_filter.filter_file(
                diff.b_blob.name, diff.b_blob.path)
            yield GitFileDiff(diff, hide_base_file, hide_current_file)


class GitFileInfo(IFileInfo):
    def __init__(self, blob: Blob):
        self._blob = blob

    @property
    def name(self) -> str:
        return self._blob.name

    @property
    def path(self) -> str:
        return self._blob.path

    @property
    def size(self) -> int:
        return self._blob.size

    @property
    def raw_content(self) -> bytes:
        return self._blob.data_stream.read()

    def get_content_text(self, encoding: str = 'utf-8') -> str:
        with TextIOWrapper(self._blob.data_stream, encoding, "replace") as t:
            return t.read()

    @property
    def raw_content_stream(self):
        return self._blob.data_stream


class GitFileDiff(IFileDiff):
    _LAZY_SENTINEL = object()

    def __init__(self, diff: Diff, hide_old_file: bool = False, hide_new_file: bool = False):
        """
        params
            hide_old_file: whether to treat the old file as if it does not exist in base commit.
            hide_new_file: whether to treat the new file as if it does not exist in current commit.
        """
        assert not hide_old_file or not hide_new_file
        self._diff = diff
        self._old_file = GitFileDiff._LAZY_SENTINEL if not hide_old_file and diff.a_blob else None
        self._new_file = GitFileDiff._LAZY_SENTINEL if not hide_new_file and diff.b_blob else None
        self._patch_applicable = not hide_old_file and not hide_new_file
        self._operation = FileDiffOperation.Unchanged
        if hide_old_file or diff.new_file:
            self._operation |= FileDiffOperation.Added
        if hide_new_file or diff.deleted_file:
            self._operation |= FileDiffOperation.Deleted
        if not hide_old_file and not hide_new_file and diff.renamed_file:
            # GitPython ensured two Blob objects have different paths, even if they shares the same blob.
            assert diff.a_blob.path != diff.b_blob.path
            self._operation |= FileDiffOperation.Renamed
        if not hide_old_file and not hide_new_file and diff.a_blob and diff.b_blob and diff.a_blob != diff.b_blob:
            self._operation |= FileDiffOperation.Modified

    @property
    def old_file(self) -> IFileInfo:
        if self._old_file is GitFileDiff._LAZY_SENTINEL:
            self._old_file = GitFileInfo(self._diff.a_blob)
        return self._old_file

    @property
    def new_file(self) -> IFileInfo:
        if self._new_file is GitFileDiff._LAZY_SENTINEL:
            self._new_file = GitFileInfo(self._diff.b_blob)
        return self._new_file

    @property
    def operation(self):
        return self._operation

    @property
    def patch(self):
        if not self._patch_applicable:
            raise NotImplementedError(
                "patch is not supported for partial diff view. (a or b side is hidden by filter.)")
        return self._diff.diff
