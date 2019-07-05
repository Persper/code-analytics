"""
call_commit_graph.py
====================================
CallCommitGraph stores all relevant analysis results
"""
import logging
import community
import networkx as nx
from networkx.readwrite import json_graph
from typing import Union, Set, List, Dict, Optional

from persper.analytics.devrank import devrank
from persper.analytics.score import normalize
from persper.analytics.complexity import eval_project_complexity

_logger = logging.getLogger(__name__)


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
    """
    The key data structure that stores all functions' call relationships
    and edit histories across commits.
    """

    def __init__(self, graph_data: Optional[Dict] = None, commit_id_generator=CommitIdGenerators.fromHexsha):
        if graph_data:
            self._digraph = json_graph.node_link_graph(
                CallCommitGraph._to_networkx_format(graph_data))
        else:
            self._digraph = self._new_graph()
        self._commit_id_generator = commit_id_generator
        self._current_commit_id = None

    @staticmethod
    def _to_networkx_format(graph_data: Dict) -> Dict:
        graph_data['multigraph'] = False
        graph_data['directed'] = True
        for node in graph_data['nodes']:
            node['files'] = set(node['files'])
        return graph_data

    def reset(self):
        """Reset all internal states"""
        self._digraph = self._new_graph()
        self._digraph.degree()

    def _new_graph(self):
        """Create a new nx.DiGraph for underlying storage
           with appropriate arguments"""
        return nx.DiGraph(commits={})

    def nodes(self, data=False):
        """Provide read-only access for nodes"""
        return self._digraph.nodes(data=data)

    def edges(self, data=False):
        """Provide read-only access for edges"""
        return self._digraph.edges(data=data)

    def commits(self):
        """Provide read-only access for commits"""
        # https://networkx.github.io/documentation/stable/tutorial.html#graph-attributes
        return self._digraph.graph['commits']

    def files(self, node: str) -> Set[str]:
        """Provide read-only access to `files` attribute of a node"""
        return self.nodes()[node]['files']

    def __contains__(self, node):
        """Implement membership check"""
        return node in self._digraph

    def add_commit(self, hexsha, author_name, author_email, message):
        # TODO: remove `id` in a commit object
        self._current_commit_id = self._commit_id_generator(self._next_cindex(), hexsha, message)
        self._digraph.graph['commits'][hexsha] = {
            'id': self._current_commit_id,
            'hexsha': hexsha,
            'authorName': author_name,
            'authorEmail': author_email,
            'message': message
        }

    # The index of the commit being analyzed
    def _cur_cindex(self):
        return len(self.commits()) - 1

    def _next_cindex(self):
        return self._cur_cindex() + 1

    # TODO: remove the default value of files
    def add_node(self, node: str, files: Union[Set[str], List[str]] = []):
        if node is None:
            _logger.error("Argument node is None in add_node.")
            return
        self._digraph.add_node(node, size=None, history={}, files=set(files))

    # add_node must be called on source and target first
    def add_edge(self, source, target):
        if source is None or target is None:
            _logger.error("Argument source or target is None in add_edge.")
            return
        if source not in self._digraph:
            raise ValueError("Error: caller %s does not exist in call-commit graph." % source)
        if target not in self._digraph:
            raise ValueError("Error: callee %s does not exist in call-commit graph." % target)
        self._digraph.add_edge(source, target,
                               addedBy=self._current_commit_id,
                               weight=None)

    def update_node_history(self, node, num_adds, num_dels):
        node_history = self._get_node_history(node)
        # A commit might update a node's history more than once when
        # a single FunctionNode corresponds to more than one actual functions
        if self._current_commit_id in node_history:
            node_history[self._current_commit_id]['adds'] += num_adds
            node_history[self._current_commit_id]['dels'] += num_dels
        else:
            node_history[self._current_commit_id] = {'adds': num_adds, 'dels': num_dels}

    def update_node_history_accurate(self, node, fstat):
        node_history = self._get_node_history(node)
        # A commit might update a node's history more than once when
        # a single FunctionNode corresponds to more than one actual functions
        if self._current_commit_id in node_history:
            node_history[self._current_commit_id]['adds'] += fstat['adds']
            node_history[self._current_commit_id]['dels'] += fstat['dels']
            node_history[self._current_commit_id]['added_units'] += fstat['added_units']
            node_history[self._current_commit_id]['removed_units'] += fstat['removed_units']
        else:
            node_history[self._current_commit_id] = {'adds': fstat['adds'], 'dels': fstat['dels'],
                                                     'added_units': fstat['added_units'], 'removed_units': fstat['removed_units']}

    # read/write access to node history are thourgh this function
    def _get_node_history(self, node: str) -> Dict[str, Dict[str, int]]:
        if node is None:
            _logger.error("Argument node is None in _get_node_history.")
            return {}
        return self._digraph.nodes[node]['history']

    def get_node_dev_eq(self, node: str, commit_black_list: Optional[Set] = None) -> int:
        """Return a function node's development equivalent (dev eq), computed from its node history
        This serves as an interface function since the underlying dev eq algorithm might change.

        Args:
                         node - A str, the node's name
            commit_black_list - A set of strs, each element is a commit's hexsha

        Returns:
            An int representing the node's dev eq
        """
        node_commits_dev_eq = self.get_node_commits_dev_eq(node, commit_black_list=commit_black_list)
        dev_eq = sum(node_commits_dev_eq.values())

        # take max between dev_eq and 1 to avoid zero division error
        return max(dev_eq, 1)

    def get_node_commits_dev_eq(self, node: str, commit_black_list: Optional[Set] = None) -> Dict[str, int]:
        """Return a function node's development equivalent, broken down into each commit's contribution.

        Args:
                         node - A str, the node's name
            commit_black_list - A set of strs, each element is a commit's hexsha

        Returns:
            A dict with keys being commit hexshas and values being how much this commit
                contributes to the node's overall dev eq.

                Note: this dict can be an empty dict for built-in functions that don't have edit history.
                Also Note: only commits that have non-zero dev eq for this node and aren't present
                    in the `commit_black_list` will be present in the returned dict
        """
        def _compute_node_commit_dev_eq(hist_entry):
            # use logical units if possible, otherwise fall back to LOC
            if 'added_units' in hist_entry.keys() and 'removed_units' in hist_entry.keys():
                return hist_entry['added_units'] + hist_entry['removed_units']
            else:
                return hist_entry['adds'] + hist_entry['dels']

        node_commits_dev_eq = {}
        node_history = self._get_node_history(node)
        for hexsha, hist_entry in node_history.items():
            if commit_black_list is not None and hexsha in commit_black_list:
                continue
            node_commits_dev_eq[hexsha] = _compute_node_commit_dev_eq(hist_entry)
        return node_commits_dev_eq

    def get_commits_dev_eq(self, commit_black_list: Optional[Set] = None) -> Dict[str, int]:
        """Return all commits' overall development equivalent

        Args:
                         node - A str, the node's name
            commit_black_list - A set of strs, each element is a commit's hexsha

        Returns:
            A dict with keys being commit hexshas and values being how much this commit
                contributes to the node's overall dev eq.

                Note: all commits are guaranteed to be present in the returned dict,
                even if their dev eq is 0 or they're present in the `commit_black_list`
        """
        commits_dev_eq = {}
        # guarantee to return all commits
        for hexsha in self.commits():
            commits_dev_eq[hexsha] = 0

        for node in self.nodes():
            node_commits_dev_eq = self.get_node_commits_dev_eq(node, commit_black_list=commit_black_list)
            for hexsha, node_commit_dev_eq in node_commits_dev_eq.items():
                commits_dev_eq[hexsha] += node_commit_dev_eq
        return commits_dev_eq

    def update_node_files(self, node: str, new_files: Union[Set[str], List[str]]):
        if node is None:
            _logger.error("Argument node is None in update_node_files")
            return
        self._digraph.nodes[node]['files'] = set(new_files)

    # TODO: provide other options for computing a node's size
    def _set_all_nodes_size(self, black_set=None):
        """ Compute node size after nodes have been added to the graph
        node size is currently defined as the total number lines of edits

        black_set - A set of commit hexshas to be blacklisted
        """
        for node in self.nodes():
            self._set_node_size(node, self.get_node_dev_eq(node))

    def _set_node_size(self, node, size):
        if node is None:
            _logger.error("Argument node is None in _set_node_size.")
        # set node size even if it is None since we'd like to suppress the error
        self._digraph.nodes[node]['size'] = size

    def _set_all_edges_weight(self):
        self._set_all_nodes_size()
        for node in self.nodes():
            for nbr, datadict in self._digraph.pred[node].items():
                datadict['weight'] = self._digraph.nodes[node]['size']

    def eval_project_complexity(self, r_n: float, r_e: float,commit_black_list: Optional[Set] = None):
        """
        Evaluates project complexity.
        params
            r_n: The conversion factor from node count to logic units.
            r_e: The conversion factor from edge count to logic units.
        """
        return eval_project_complexity(self._digraph, r_n, r_e,commit_black_list)

    def _remove_invalid_nodes(self):
        if None in self.nodes():
            self._digraph.remove_node(None)

    def function_devranks(self, alpha, black_set=None):
        """
        Args:
                alpha - A float between 0 and 1, commonly set to 0.85
            black_set - A set of commit hexshas to be blacklisted

        Returns:
            A dict with keys being function IDs and values being devranks
        """
        self._remove_invalid_nodes()
        self._set_all_nodes_size(black_set=black_set)
        return devrank(self._digraph, 'size', alpha=alpha)

    def commit_function_devranks(self, alpha, commit_black_list: Optional[Set] = None) -> Dict[str, Dict[str, float]]:
        """Show how a commit's devrank can be broken down into the partial devranks of the functions it changed
            Here is the formula for how much devrank commit c receives by changing function f:

                dr(c, f) = dr(f) * dev_eq(f, c) / dev_eq(f)

        Args:
                alpha - A float between 0 and 1, commonly set to 0.85
            black_set - A set of commit hexshas to be blacklisted

        Returns:
            A dict with keys being commit hexshas and values being dicts,
                whose values are function IDs and values are devranks

            Note: all commits are guaranteed to be present in the returned dict,
            even if they didn't touch any function (thus have an empty dict)
        """
        commit_function_devranks = {}
        # guarantee to return all commits
        for hexsha in self.commits():
            commit_function_devranks[hexsha] = {}

        func_devranks = self.function_devranks(alpha, black_set=commit_black_list)

        for func in self.nodes():
            func_commits_dev_eq = self.get_node_commits_dev_eq(func, commit_black_list=commit_black_list)
            # skip this node if empty (it's probably a built-in function or third-party dep)
            if len(func_commits_dev_eq) == 0:
                continue

            func_dev_eq = self.get_node_dev_eq(func, commit_black_list=commit_black_list)
            for hexsha, func_commit_dev_eq in func_commits_dev_eq.items():
                func_commit_dr = (func_commit_dev_eq / func_dev_eq) * func_devranks[func]
                commit_function_devranks[hexsha][func] = func_commit_dr

        return commit_function_devranks

    def commit_devranks(self, alpha, black_set: Optional[Set] = None):
        """Computes all commits' devranks from function-level devranks
            Here is the formula:

                dr(c) = sum(dr(c, f) for f in C_f)

            where dr(*) is the devrank function, dev_eq(*, *) is the development equivalent function,
            and C_f is the set of functions that commit c changed.

        Args:
                alpha - A float between 0 and 1, commonly set to 0.85
            black_set - A set of commit hexshas to be blacklisted

        Returns:
            A dict with keys being commit hexshas and values being commit devranks

                Note: all commits are guaranteed to be present in the returned dict,
                even if their devrank is 0 or they're present in the `black_set`
        """
        commit_devranks = {}
        commit_function_devranks = self.commit_function_devranks(alpha, commit_black_list=black_set)
        for hexsha, commit_dict in commit_function_devranks.items():
            commit_devranks[hexsha] = sum(commit_dict.values())
        return commit_devranks

    def developer_devranks(self, alpha, black_set=None):
        """
        Args:
                alpha - A float between 0 and 1, commonly set to 0.85
            black_set - A set of commit hexshas to be blacklisted
        """
        developer_devranks = {}
        commit_devranks = self.commit_devranks(alpha, black_set=black_set)

        for commit in self.commits().values():
            sha = commit['hexsha']
            email = commit['authorEmail']

            if sha not in commit_devranks:
                continue

            if email in developer_devranks:
                developer_devranks[email] += commit_devranks[sha]
            else:
                developer_devranks[email] = commit_devranks[sha]
        return developer_devranks

    def compute_modularity(self):
        """Compute modularity score based on function graph.

        Returns
        -------
            modularity : float
                The modularity score of this graph.
        """
        # Check the number of edges
        if len(self.edges()) == 0:
            return 0.

        # Construct non directed graph
        graph = nx.Graph()
        for node in self.nodes():
            if node is not None:
                graph.add_node(node)
        for (source, target) in self.edges():
            if source is not None and target is not None:
                graph.add_edge(source, target)
        # Compute the partition of the graph nodes
        partition = community.best_partition(graph)
        # Compute modularity
        modularity = community.modularity(partition, graph)
        # Normalize [0, 1] to [0, 100]
        modularity = modularity * 100

        return modularity
