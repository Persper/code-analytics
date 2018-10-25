from numpy import linalg as LA
import numpy as np
from scipy.sparse import coo_matrix


def pagerank(G, alpha=0.85, epsilon=1e-5, max_iters=300):
    """Memory efficient PageRank using scipy.sparse
    This function implements Algo 1. in "A Survey on PageRank Computing"
    """
    ni = {}
    for i, u in enumerate(G):
        ni[u] = i

    num_nodes = len(G.nodes())

    row, col, data = [], [], []
    for u in G:
        num_out_edges = len(G[u])
        if num_out_edges > 0:
            w = 1 / num_out_edges
            for v in G[u]:
                row.append(ni[v])
                col.append(ni[u])
                data.append(w)

    P = coo_matrix((data, (row, col)), shape=(num_nodes, num_nodes)).tocsr()
    p = np.ones(num_nodes) / num_nodes
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
