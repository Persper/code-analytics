import numpy as np
from numpy import linalg as LA
from scipy.sparse import coo_matrix


def devrank(G, weight_label, alpha=0.85, epsilon=1e-5, max_iters=300):
    """Memory efficient DevRank using scipy.sparse

    Args:
                   G - A nx.Digraph object.
        weight_label - A string, each node in graph should have this attribute.
                     - It will be used as the weight of each node.
               alpha - A float between 0 and 1, DevRank's damping factor.
             epsilon - A float.
           max_iters - An integer, specify max number of iterations to run.

    Returns:
        A dict with node names being keys and DevRanks being values.
    """
    ni = {}
    for i, u in enumerate(G):
        ni[u] = i

    def sizeof(u):
        return G.node[u][weight_label]

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
