import os
import re
import requests
from persper.graphs.patch_parser import PatchParser
from networkx.readwrite import json_graph

default_regex_strs = [
    '.+\.js$',
    '^(?!dist/).+',
    '^(?!test(s)?/).+',
    '^(?!spec/).+',
    '^(?!build/).+',
    '^(?!bin/).+',
    '^(?!doc(s)?/).+'
]

def regexes_from_strs(regex_strs):
    return [re.compile(regex_str) for regex_str in regex_strs]


class JSGraph():

    def __init__(self, server_addr, fname_regex_strs=None, server_config={}):
        self.parser = PatchParser()
        if fname_regex_strs:
            self.fname_regexes = regexes_from_strs(fname_regex_strs)
        else:
            self.fname_regexes = regexes_from_strs(default_regex_strs)
        self.server_addr = server_addr
        self.server_config = server_config

    def update_graph(self, old_fname, old_src, new_fname, new_src, patch):
        payload = {'oldFname': old_fname,
                   'oldSrc': old_src,
                   'newFname': new_fname,
                   'newSrc': new_src,
                   'patch': patch.decode('utf-8', 'replace'),
                   'config': self.server_config }

        update_url = os.path.join(self.server_addr, 'update')
        r = requests.post(update_url, json=payload)
        res = r.json()
        return res['idToLines'], res['idMap']

    def get_change_stats(self, old_fname, old_src, new_fname, new_src, patch):
        payload = {'oldFname': old_fname,
                   'oldSrc': old_src,
                   'newFname': new_fname,
                   'newSrc': new_src,
                   'patch': patch.decode('utf-8', 'replace'),
                   'config': self.server_config }

        stats_url = os.path.join(self.server_addr, 'stats')
        r = requests.get(stats_url, json=payload)
        res = r.json()
        return res['idToLines'], res['idMap']

    def get_graph(self):
        graph_url = os.path.join(self.server_addr, 'callgraph')
        r = requests.get(graph_url)
        return json_graph.node_link_graph(r.json())

    def reset_graph(self):
        reset_url = os.path.join(self.server_addr, 'reset')
        requests.post(reset_url)

    def fname_filter(self, fname):
        # Takes the intersection of the regexes
        for regex in self.fname_regexes:
            if not regex.match(fname):
                return False
        return True
