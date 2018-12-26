import networkx as nx
from networkx.readwrite import json_graph
from persper.analytics.devrank import devrank


def normalize(devranks):
    normalized_devranks = {}
    dr_sum = 0
    for _, dr in devranks.items():
        dr_sum += dr

    for idx in devranks:
        normalized_devranks[idx] = devranks[idx] / dr_sum
    return normalized_devranks


class CallCommitGraph:

    def __init__(self, node_link_data=None):
        if node_link_data:
            self._digraph = json_graph.node_link_graph(node_link_data)
        else:
            self._digraph = nx.DiGraph(commitList=[])

    # Read-only access
    def nodes(self, data=False):
        return self._digraph.nodes(data=data)

    # Read-only access
    def edges(self, data=False):
        return self._digraph.edges(data=data)

    # Read-only access
    def commits(self):
        # https://networkx.github.io/documentation/stable/tutorial.html#graph-attributes
        return self._digraph.graph['commitList']

    def add_commit(self, hexsha, author_name, author_email, commit_message):
        self._digraph.graph['commitList'].append({
            'hexsha': hexsha, 'authorName': author_name,
            'authorEmail': author_email, 'message': commit_message
        })

    # The index of the commit being analyzed
    def _cur_cindex(self):
        return len(self.commits()) - 1

    def reset(self):
        self._digraph = nx.DiGraph(commitList=[])

    def __contains__(self, node):
        return node in self._digraph

    def add_node(self, node):
        self._digraph.add_node(node, size=0, history={})

    # add_node must be called on source and target first
    def add_edge(self, source, target):
        self._digraph.add_edge(source, target,
                               addedBy=self._cur_cindex(),
                               weight=self._digraph.nodes[target]['size'])

    def update_node_history(self, node, size):
        # Use current commit index
        cc_idx = self._cur_cindex()
        node_history = self._digraph.nodes[node]['history']
        # A commit might update a node's history more than once
        if cc_idx in node_history:
            node_history[cc_idx] += size
        else:
            node_history[cc_idx] = size
        self._update_node_size(node, size)
        self._update_ingoing_weight(node)
        self._check_history_match_size(node)

    # node's size is automatically updated when history is updated
    def _update_node_size(self, node, size):
        self._digraph.nodes[node]['size'] += size

    # edge's weight is automaitcally updated when history is updated
    # needs to be called after _update_node_size
    def _update_ingoing_weight(self, node):
        for nbr, datadict in self._digraph.pred[node].items():
            datadict['weight'] = self._digraph.nodes[node]['size']

    def _check_history_match_size(self, node):
        assert(sum(self._digraph.nodes[node]['history'].values()) ==
               self._digraph.nodes[node]['size'])

    def function_devranks(self, alpha):
        return devrank(self._digraph, 'size', alpha=alpha)

    def commit_devranks(self, alpha):
        commit_devranks = {}
        func_devranks = self.function_devranks(alpha)

        for func, data in self.nodes(data=True):
            size = data['size']
            history = data['history']

            if len(history) == 0:
                continue

            for cindex, csize in history.items():
                sha = self.commits()[cindex]['hexsha']
                dr = (csize / size) * func_devranks[func]
                if sha in commit_devranks:
                    commit_devranks[sha] += dr
                else:
                    commit_devranks[sha] = dr

        return commit_devranks

    def developer_devranks(self, alpha):
        developer_devranks = {}
        commit_devranks = self.commit_devranks(alpha)

        for commit in self.commits():
            sha = commit['hexsha']
            email = commit['authorEmail']

            if sha not in commit_devranks:
                continue

            if email in developer_devranks:
                developer_devranks[email] += commit_devranks[sha]
            else:
                developer_devranks[email] = commit_devranks[sha]
        return developer_devranks
