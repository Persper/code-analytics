import numpy as np
from numpy import linalg as LA

def devrank(G, count_self=False, alpha=0.85, epsilon=1e-5, max_iters=300):
    ni = {}
    for i, u in enumerate(G):
        ni[u] = i
        
    sizes = {}
    universe_size = 0
    for u in G:
        sizes[u] = G.node[u]['num_lines']
        universe_size += sizes[u]
        
    num_nodes = len(G.nodes())
    P = np.zeros([num_nodes, num_nodes])
    
    for u in G:
        num_out_edges = len(G[u])
        if num_out_edges == 0:
            P[:, ni[u]] = 1 / num_nodes
        else:
            total_out_sizes = 0
            for v in G[u]:
                total_out_sizes += sizes[v]
            if count_self:
                total_out_sizes += sizes[u]
                P[ni[u], ni[u]] = sizes[u] / total_out_sizes
            for v in G[u]:
                P[ni[v], ni[u]] = sizes[v] / total_out_sizes
            
    p = np.empty(num_nodes)
    for u in G:
        p[ni[u]] = sizes[u] / universe_size

    v = np.ones(num_nodes) / num_nodes
        
    for i in range(max_iters):
        new_v = alpha * np.dot(P, v) + (1 - alpha) * p
        assert(new_v.shape == (num_nodes,))
        delta = new_v - v
        if LA.norm(delta) < epsilon:
            break
        v = new_v
        
    pr = {}
    for u in G:
        pr[u] = v[ni[u]]
    
    return pr