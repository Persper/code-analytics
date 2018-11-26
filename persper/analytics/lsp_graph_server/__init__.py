from persper.analytics.patch_parser import PatchParser
from persper.analytics.graph_server import GraphServer
from persper.analytics.call_commit_graph import CallCommitGraph


class LspClientGraphServer(GraphServer):
    def __init__(self, filename_regex_strs):
        pass

    def register_commit(self, hexsha, author_name, author_email, commit_message):
        pass

    def update_graph(self, old_filename: str, old_src: str,
                     new_filename: str, new_src: str, patch: bytes):
        pass

    def get_graph(self):
        pass

    def reset_graph(self):
        pass

    def filter_file(self, filename):
        pass

    def config(self, param: dict):
        pass
