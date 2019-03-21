from networkx.readwrite import json_graph
from persper.analytics.graph_server import GraphServer, CommitSeekingMode
from persper.analytics.call_commit_graph import CallCommitGraph
import re
import requests
import urllib.parse
from persper.analytics.error import GraphServerError


class GraphServerStateRecoveryError(GraphServerError):
    pass


class GoGraphServer(GraphServer):
    def __init__(self, server_addr, filename_regex_strs):
        self.server_addr = server_addr
        self.filename_regexes = [re.compile(regex_str) for regex_str in filename_regex_strs]
        self.config_param = dict()
        self._session = requests.Session()

    def __getstate__(self):
        state = self.__dict__.copy()
        del state['_session']
        state['server_state'] = self._get_server_state()
        return state

    def _get_server_state(self):
        """Request the server to dump all internal state

        Right now, the call-commit graph contains all info we need for resetting state.
        """
        return self.get_graph()

    def __setstate__(self, state):
        self.server_addr = state['server_addr']
        self.filename_regexes = state['filename_regexes']
        self.config_param = state['config_param']
        self._set_server_state(state['server_state'])

    def _set_server_state(self, server_state):
        payload = {'serverState': server_state}
        url = urllib.parse.urljoin(self.server_addr, '/set_server_state')
        r = self._session.post(url, json=payload).json()
        if r != '0':
            raise GraphServerStateRecoveryError('Failed to set golang server state.')

    def start_commit(self, hexsha: str, seeking_mode: CommitSeekingMode, author_name: str,
                     author_email: str, commit_message: str):
        payload = {
            'hexsha': hexsha,
            'authorEmail': author_email,
            'authorName': author_name,
            'message': commit_message,
            'seekingMode': seeking_mode.value,
        }
        register_url = urllib.parse.urljoin(self.server_addr, '/start_commit')
        r = self._session.post(register_url, json=payload).json()
        if r != '0':
            raise ValueError()

    def register_commit(self, hexsha, author_name, author_email, commit_message):
        # TODO: use 'message' or 'commit_message', but not both
        payload = {
            'hexsha': hexsha,
            'authorEmail': author_email,
            'authorName': author_name,
            'message': commit_message,
        }
        register_url = urllib.parse.urljoin(self.server_addr, '/register_commit')
        r = self._session.post(register_url, json=payload).json()
        if r != '0':
            raise ValueError()

    def update_graph(self, old_filename, old_src,
                     new_filename, new_src, patch):
        payload = {'oldFname': old_filename,
                   'oldSrc': old_src,
                   'newFname': new_filename,
                   'newSrc': new_src,
                   'patch': patch.decode('utf-8', 'replace'),
                   'config': self.config_param}

        update_url = urllib.parse.urljoin(self.server_addr, '/update')
        r = self._session.post(update_url, json=payload).json()
        if r != '0':
            raise ValueError()

    def get_graph(self):
        graph_url = self.server_addr + '/callgraph'
        r = self._session.get(graph_url)
        return CallCommitGraph(graph_data=r.json())

    def reset_graph(self):
        reset_url = urllib.parse.urljoin(self.server_addr, '/reset')
        self._session.post(reset_url)

    def filter_file(self, filename):
        for regex in self.filename_regexes:
            if not regex.match(filename):
                return False
        return True

    def config(self, param):
        self.config_param = param
