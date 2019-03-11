import networkx as nx
from persper.analytics.devrank import devrank


def test_devrank():
    G = nx.DiGraph()
    G.add_node(1, weight=10)
    G.add_node(2, weight=10)
    G.add_edge(1, 2)
    G.add_edge(2, 1)
    assert devrank(G, 'weight') == {1: 0.5, 2: 0.5}

    G2 = nx.DiGraph()
    G2.add_edges_from([(1, 2), (2, 3), (3, 4), (4, 1)])
    for u in G2:
        G2.node[u]['weight'] = 10
    assert devrank(G2, 'weight') == {1: 0.25, 2: 0.25, 3: 0.25, 4: 0.25}

    G3 = nx.DiGraph()
    G3.add_edge(1, 2)
    for u in G3:
        G3.node[u]['weight'] = 10
    dr = devrank(G3, 'weight', alpha=1.0)
    assert abs(dr[1] - 0.3333) < 0.0001
    assert abs(dr[2] - 0.6666) < 0.0001
