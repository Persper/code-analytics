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


class CommitIdGenerators:
    @staticmethod
    def fromOrdinal(ordinal: int, hexsha: str, message: str):
        return ordinal

    @staticmethod
    def fromComment(ordinal: int, hexsha: str, message: str):
        return message.strip()

    @staticmethod
    def fromHexsha(ordinal: int, hexsha: str, message: str):
        return hexsha


class CallCommitGraph:

    def __init__(self, node_link_data=None, commit_id_generator=CommitIdGenerators.fromOrdinal):
        if node_link_data:
            self._digraph = json_graph.node_link_graph(node_link_data)
        else:
            self._digraph = nx.DiGraph(commitList=[])
        self._commit_id_generator = commit_id_generator
        self._current_commit_id = None

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
        self._current_commit_id = self._commit_id_generator(self._next_cindex(), hexsha, commit_message)
        self._digraph.graph['commitList'].append({
            'id': self._current_commit_id,
            'hexsha': hexsha, 'authorName': author_name,
            'authorEmail': author_email, 'message': commit_message
        })

    # The index of the commit being analyzed
    def _cur_cindex(self):
        return len(self.commits()) - 1

    def _next_cindex(self):
        return self._cur_cindex() + 1

    def reset(self):
        self._digraph = nx.DiGraph(commitList=[])

    def __contains__(self, node):
        return node in self._digraph

    def add_node(self, node):
        self._digraph.add_node(node, size=None, history={})

    # add_node must be called on source and target first
    def add_edge(self, source, target):
        self._digraph.add_edge(source, target,
                               addedBy=self._current_commit_id,
                               weight=None)

    def update_node_history(self, node, size):
        node_history = self._get_node_history(node)
        # A commit might update a node's history more than once
        if self._current_commit_id in node_history:
            node_history[self._current_commit_id] += size
        else:
            node_history[self._current_commit_id] = size

    # read/write access to node history are thourgh this function
    def _get_node_history(self, node):
        return self._digraph.nodes[node]['history']

    def _set_all_nodes_size(self, black_set=None):
        """ Compute node size after nodes have been added to the graph
        node size is currently defined as the total number lines of edits

        black_set - A set of commit hexshas to be blacklisted
        """
        for node in self.nodes():
            node_history = self._get_node_history(node)
            if black_set is not None:
                size = 0
                for cindex, csize in node_history.items():
                    sha = self.commits()[cindex]['hexsha']
                    if sha not in black_set:
                        size += csize
            else:
                size = sum(node_history.values())

            # set default size to 1 to avoid zero division error
            if size == 0:
                size = 1
            self._set_node_size(node, size)

    def _set_node_size(self, node, size):
        self._digraph.nodes[node]['size'] = size

    def _set_all_edges_weight(self):
        self._set_all_nodes_size()
        for node in self.nodes():
            for nbr, datadict in self._digraph.pred[node].items():
                datadict['weight'] = self._digraph.nodes[node]['size']

    def function_devranks(self, alpha, black_set=None):
        """
        Args:
                alpha - A float between 0 and 1, commonly set to 0.85
            black_set - A set of commit hexshas to be blacklisted
        """
        self._set_all_nodes_size(black_set=black_set)
        return devrank(self._digraph, 'size', alpha=alpha)

    def commit_devranks(self, alpha, black_set=None):
        """
        Args:
                alpha - A float between 0 and 1, commonly set to 0.85
            black_set - A set of commit hexshas to be blacklisted
        """
        commit_devranks = {}
        func_devranks = self.function_devranks(alpha, black_set=black_set)

        for func, data in self.nodes(data=True):
            size = data['size']
            history = data['history']

            if len(history) == 0:
                continue

            for cindex, csize in history.items():
                sha = self.commits()[cindex]['hexsha']
                if black_set is None or sha not in black_set:
                    dr = (csize / size) * func_devranks[func]
                    if sha in commit_devranks:
                        commit_devranks[sha] += dr
                    else:
                        commit_devranks[sha] = dr

        return commit_devranks

    def developer_devranks(self, alpha, black_set=None):
        """
        Args:
                alpha - A float between 0 and 1, commonly set to 0.85
            black_set - A set of commit hexshas to be blacklisted
        """
        developer_devranks = {}
        commit_devranks = self.commit_devranks(alpha, black_set=black_set)

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
