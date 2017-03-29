from numpy import linalg as LA
import numpy as np

def pagerank(G, alpha=0.85, epsilon=1e-5, max_iters=300):
    ni = {}
    for i, u in enumerate(G):
        ni[u] = i
        
    num_nodes = len(G.nodes())
    P = np.zeros([num_nodes, num_nodes])
    
    for u in G:
        num_out_edges = len(G[u])
        if num_out_edges == 0:
            P[:, ni[u]] = 1 / num_nodes
        else:
            for v in G[u]:
                P[ni[v], ni[u]] = 1 / num_out_edges
            
    p = np.ones(num_nodes) / num_nodes
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