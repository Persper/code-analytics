import numpy as np
from numpy import linalg as LA
from scipy.sparse import coo_matrix


def devrank(G, count_self=False, alpha=0.85, epsilon=1e-5, max_iters=300):
    """Memory efficient DevRank using scipy.sparse"""
    ni = {}
    for i, u in enumerate(G):
        ni[u] = i

    def sizeof(u):
        return G.node[u]['num_lines']

    num_nodes = len(G.nodes())
    row, col, data = [], [], []
    for u in G:
        num_out_edges = len(G[u])
        if num_out_edges > 0:
            total_out_sizes = 0
            for v in G[u]:
                total_out_sizes += sizeof(v)
            if count_self:
                total_out_sizes += sizeof(u)
                row.append(ni[u])
                col.append(ni[u])
                data.append(sizeof(u) / total_out_sizes)
            for v in G[u]:
                row.append(ni[v])
                col.append(ni[u])
                data.append(sizeof(v) / total_out_sizes)

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

    pr = {}
    for u in G:
        pr[u] = v[ni[u]]

    return pr
