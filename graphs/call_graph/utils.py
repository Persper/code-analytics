def transform_node_to_src(node, s=None):
    """Print out the source code of a xml node"""
    if s == None:
        s = ""
    if node.text:
        s += node.text
    for child in node:
        s = transform_node_to_src(child, s)
    if node.tail:
        s += node.tail
    return s