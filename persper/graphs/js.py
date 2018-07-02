import os
import requests
from persper.graphs.patch_parser import PatchParser
from networkx.readwrite import json_graph


class JSGraph():

    def __init__(self, server_addr):
        self.parser = PatchParser()
        self.exts = ('.js',)
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
