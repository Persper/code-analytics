import matplotlib as mpl
import matplotlib.cm as cm


def map_to_color(x, m):
    color_list = [int(255 * c) for c in m.to_rgba(x)]
    return '#%02x%02x%02x%02x' % tuple(color_list)
        
def write_G_to_dot_with_pr(G, pr, fname, edge_attrib=None, header_lines=None):
    norm = mpl.colors.Normalize(vmin=min(pr.values()), vmax=max(pr.values()))
    cmap = cm.Blues
    m = cm.ScalarMappable(norm, cmap=cmap)
    with open(fname, 'w+') as f:
        f.write('digraph graphname {\n')
        if header_lines:
            for line in header_lines:
                f.write(line)
        for n in G.nodes_iter(data=False):
            color_str = map_to_color(pr[n], m)
            f.write('\"{}\" [style=filled fillcolor="{}" tooltip=\"{}\"];\n'.format(n, color_str, pr[n]))
        for e in G.edges_iter(data=True):
            if edge_attrib:
                f.write('\"{}\" -> \"{}\" [ label=\"{}\"];\n'.format(e[0], e[1], '&#10;'.join(e[2][edge_attrib][:10])))
            else:
                f.write('\"{}\" -> \"{}\";\n'.format(e[0], e[1]))
        
        f.write('}')