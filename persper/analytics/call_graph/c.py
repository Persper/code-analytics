import networkx as nx
from persper.graphs.call_graph.utils import remove_edges_of_node, ns, line_attr


class NotFunctionCallError(Exception):
    """Raise for false positive <call> nodes"""


def handle_function(func_node):
    """Given a <function> node,
    return function name and function range (start & end lineno)"""

    name_node = func_node.find('srcml:name', ns)
    func_name, start_line = handle_name(name_node)
    if not func_name or not start_line:
        print('Function name/start not found!')  # very unlikely to happen
        return None, None, None

    block_node = func_node.find('srcml:block', ns)
    if block_node is None:
        try:
            block_node = func_node.xpath('./following-sibling::srcml:block',
                                         namespaces=ns)[0]
        except:
            print("Block node not found (in func {})".format(func_name))
            return func_name, None, None
    try:
        pos_node = block_node.find('pos:position', ns)
        end_line = int(pos_node.attrib[line_attr])
    except:
        print("Block node doesn't have position node inside!")
        return func_name, None, None

    return func_name, start_line, end_line


def handle_name(name_node):
    """Given an <name> node,
    return its text content and position (line)"""
    text, line = None, None
    if name_node is not None:
        text = name_node.text
        line = int(name_node.attrib[line_attr])
    return text, line


def handle_call(call_node):
    """Given an <call> node, return function name being called

    Throws NotFunctionCallException

    Case 1: casting function pointer is not function call
        Example: tmp.sa_handler = (void (*)(int)) handler;

    Case 2: function call from struct variable
        Example: tty->write(tty)

    """
    name_node = call_node.find('srcml:name', ns)
    if name_node is None:
        # Case 1
        raise NotFunctionCallError()
    callee_name = name_node.text
    if callee_name is None:
        # Case 2
        callee_name = name_node[-1].text
    return callee_name


def build_call_graph_c(roots, G=None):
    if G is None:
        G = nx.DiGraph()

    new_func = {}
    func_to_file = {}
    for root in roots:
        # print('------ ' + root.attrib['filename'] + ' ------')

        for func_node in root.findall('./srcml:function', namespaces=ns):

            caller_name, start_line, end_line = handle_function(func_node)
            if not caller_name:
                continue

            if start_line and end_line:
                num_lines = end_line - start_line + 1
            else:
                # default num_lines is 1
                num_lines = 1

            if caller_name not in G:
                # Case 1: hasn't been defined and hasn't been called
                new_func[caller_name] = num_lines
                G.add_node(caller_name, num_lines=num_lines, defined=True)
            elif not G.node[caller_name]['defined']:
                # Case 2: has been called but hasn't been defined
                new_func[caller_name] = num_lines
                G.node[caller_name]['defined'] = True
                G.node[caller_name]['num_lines'] = num_lines
            else:
                # Case 3: has been called and has been defined
                # it is modified in the latest commit
                # pass because it's not a new function
                # so no need to add it to new_func and to
                # update G.node[caller_name]['num_lines']
                pass

            func_to_file[caller_name] = root.attrib['filename']

            # handle all function calls
            for call_node in func_node.xpath('.//srcml:call', namespaces=ns):

                try:
                    callee_name = handle_call(call_node)
                except NotFunctionCallError:
                    continue
                except:
                    print("Callee name not found! (in func %s)" % caller_name)
                    continue

                if callee_name not in G:
                    G.add_node(callee_name, num_lines=1, defined=False)
                G.add_edge(caller_name, callee_name)

    return G, new_func, func_to_file


def update_call_graph_c(G, roots, modified_func):
    for func_name in modified_func:
        if func_name in G:
            remove_edges_of_node(G, func_name, in_edges=False)
            G.node[func_name]['num_lines'] += modified_func[func_name]

    # here roots should be constructed from the more recent commit
    # new functions and their sizes are stored in new_func dictionary
    _, new_func, _ = build_call_graph_c(roots, G)
    return new_func


def get_func_ranges_c(root):
    func_names, func_ranges = [], []
    for func_node in root.findall('./srcml:function', namespaces=ns):

        func_name, start_line, end_line = handle_function(func_node)
        if not (func_name and start_line and end_line):
            continue

        func_ranges.append([start_line, end_line])
        func_names.append(func_name)
    return func_names, func_ranges
