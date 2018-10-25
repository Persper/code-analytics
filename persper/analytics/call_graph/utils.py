ns = {'srcml': 'http://www.srcML.org/srcML/src',
      'pos': 'http://www.srcML.org/srcML/position'}

line_attr = '{http://www.srcML.org/srcML/position}line'


def transform_node_to_src(node, s=None):
    """Print out the source code of a xml node"""
    if s is None:
        s = ""
    if node.text:
        s += node.text
    for child in node:
        s = transform_node_to_src(child, s)
    if node.tail:
        s += node.tail
    return s


def remove_edges_of_node(G, n, in_edges=True, out_edges=True):
    """Remove edges of n, but keep the node itself in the graph

    >>> G3 = nx.DiGraph()
    >>> G3.add_path([0, 1, 2, 3, 4])
    >>> remove_edges_of_node(G3, 2)
    >>> G3.nodes()
    [0, 1, 2, 3, 4]
    >>> G3.edges()
    [(0, 1), (3, 4)]

    """
    try:
        nbrs = G._succ[n]
    except KeyError:  # NetworkXError if not in self
        # raise NetworkXError("The node %s is not in the digraph."%(n, ))
        print("The node %s is not in the digraph." % n)
        return
    if out_edges:
        for u in nbrs:
            del G._pred[u][n]
        G._succ[n] = {}
    if in_edges:
        for u in G._pred[n]:
            del G._succ[u][n]
        G._pred[n] = {}
