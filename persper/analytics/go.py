from networkx.readwrite import json_graph
from persper.analytics.graph_server import GraphServer
from persper.analytics.call_commit_graph import CallCommitGraph
import re
import requests
import urllib.parse


class GraphServerHttp(GraphServer):
    def __init__(self, server_addr, filename_regex_strs):
        self.server_addr = server_addr
        self.filename_regexes = [re.compile(regex_str) for regex_str in filename_regex_strs]
        self.config_param = dict()

    def register_commit(self, hexsha, author_name, author_email, commit_message):
        payload = {'hexsha': hexsha,
                   'author_name': author_name,
                   'author_email': author_email,
                   'commit_message': commit_message}
        register_url = urllib.parse.urljoin(self.server_addr, '/register_commit')
        r = requests.post(register_url, json=payload).json()
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
        r = requests.post(update_url, json=payload).json()
        if r != '0':
            raise ValueError()

    def get_graph(self):
        graph_url = self.server_addr + '/callgraph'
        r = requests.get(graph_url)
        return CallCommitGraph(r.json())

    def reset_graph(self):
        reset_url = urllib.parse.urljoin(self.server_addr, '/reset')
        requests.post(reset_url)

    def filter_file(self, filename):
        for regex in self.filename_regexes:
            if not regex.match(filename):
                return False
        return True

    def config(self, param):
        self.config_param = param

