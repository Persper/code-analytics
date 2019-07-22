import numpy as np
from numpy import linalg as LA
from scipy.sparse import coo_matrix
from typing import Optional, List, Tuple
import networkx as nx


def reduce_graph(G: nx.DiGraph, weight_label: str, top_in_degree: int):

    def sizeof(u):
        return G.node[u][weight_label]

    rg = nx.DiGraph()

    # replicate nodes from G
    for u in G:
        rg.add_node(u)
        rg.node[u][weight_label] = sizeof(u)

    # for each node v in G, find top k predecessors where k = top_in_degree
    for v in G:
        preds: List[Tuple[str, int]] = []
        for u in G.predecessors(v):
            preds.append((u, sizeof(u)))

        preds.sort(key=lambda x: x[1], reverse=True)
        # it is ok for `top_in_degree` to be larger than len(preds)
        for u, _ in preds[:top_in_degree]:
            rg.add_edge(u, v)

    return rg


def devrank(G: nx.DiGraph, weight_label: str, alpha: float = 0.85, epsilon: float = 1e-5,
            max_iters: int = 300, top_in_degree: Optional[int] = None):
    """Memory efficient DevRank using scipy.sparse

    Args:
                    G - A nx.Digraph object.
         weight_label - A string, each node in graph should have this attribute.
                      - It will be used as the weight of each node.
                alpha - A float between 0 and 1, DevRank's damping factor.
              epsilon - A float.
            max_iters - An integer, specify max number of iterations to run.
        top_in_degree - An `int`, if `None`, use all edges.
                      - If a value is given, then each node only receives shares from the top k nodes by size where k equals `top_in_degree`.

    Returns:
        A dict with node names being keys and DevRanks being values.
    """
    if top_in_degree:
        G = reduce_graph(G, weight_label, top_in_degree)

    ni = {}
    for i, u in enumerate(G):
        ni[u] = i

    def sizeof(u):
        return G.node[u][weight_label]

    # Phase 1: construct transition matrix P
    num_nodes = len(G.nodes())
    row, col, data = [], [], []
    for u in G:
        size_sum = 0
        for v in G[u]:
            size_sum += sizeof(v)
        for v in G[u]:
            row.append(ni[v])
            col.append(ni[u])
            data.append(sizeof(v) / size_sum)

    P = coo_matrix((data, (row, col)), shape=(num_nodes, num_nodes)).tocsr()

    universe_size = 0
    for u in G:
        universe_size += sizeof(u)

    p = np.empty(num_nodes)
    for u in G:
        p[ni[u]] = sizeof(u) / universe_size

    v = np.ones(num_nodes) / num_nodes

    for i in range(max_iters):
        new_v = alpha * P.dot(v)
        gamma = LA.norm(v, 1) - LA.norm(new_v, 1)
        new_v += gamma * p
        delta = LA.norm(new_v - v, 1)
        if delta < epsilon:
            break
        v = new_v

    dr = {}
    for u in G:
        dr[u] = v[ni[u]]

    return dr
