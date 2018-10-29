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


def update_graph(ccgraph, ast_list, change_stats):
    for ast in ast_list:
        for function in ast.findall('./srcml:function', namespaces=ns):
            caller_name, _, _ = handle_function(function)
            if not caller_name:
                continue

            if caller_name not in ccgraph:
                ccgraph.add_node(caller_name)

            for call in function.xpath('.//srcml:call', namespaces=ns):
                try:
                    callee_name = handle_call(call)
                except NotFunctionCallError:
                    continue
                except:
                    print("Callee name not found (in %s)" % caller_name)
                    continue

                if callee_name not in ccgraph:
                    ccgraph.add_node(callee_name)
                ccgraph.add_edge(caller_name, callee_name)

    for func_name, change_size in change_stats.items():
        if func_name not in ccgraph:
            print("%s in change_stats but not in ccgraph" % func_name)
            continue
        ccgraph.update_node_history(func_name, change_size)


def get_func_ranges_c(root):
    func_names, func_ranges = [], []
    for func_node in root.findall('./srcml:function', namespaces=ns):

        func_name, start_line, end_line = handle_function(func_node)
        if not (func_name and start_line and end_line):
            continue

        func_ranges.append([start_line, end_line])
        func_names.append(func_name)
    return func_names, func_ranges
