import os
import re
import requests
from persper.graphs.patch_parser import PatchParser
from networkx.readwrite import json_graph


class JSGraph():

    def __init__(self, server_addr):
        self.parser = PatchParser()
        self.fname_regexes = (re.compile('.+\.js$'),
                              re.compile('^(?!dist/).+'),
                              re.compile('^(?!test(s)?/).+'),
                              re.compile('^(?!packages/).+'),
                              re.compile('^(?!spec/).+'),
                              re.compile('^(?!build/).+'),
                              re.compile('^(?!bin/).+'),
                              re.compile('^(?!doc(s)?/).+'))
        self.server_addr = server_addr

    def update_graph(self, old_fname, old_src, new_fname, new_src, patch):
        payload = {'oldFname': old_fname,
                   'oldSrc': old_src,
                   'newFname': new_fname,
                   'newSrc': new_src,
                   'patch': patch.decode('utf-8', 'replace')}
        update_url = os.path.join(self.server_addr, 'update')
        r = requests.post(update_url, json=payload)
        res = r.json()
        return res['idToLines'], res['idMap']

    def get_change_stats(self, old_fname, old_src, new_fname, new_src, patch):
        payload = {'oldFname': old_fname,
                   'oldSrc': old_src,
                   'newFname': new_fname,
                   'newSrc': new_src,
                   'patch': patch.decode('utf-8', 'replace')}
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
