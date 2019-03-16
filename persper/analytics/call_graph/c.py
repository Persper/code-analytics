from persper.analytics.call_graph.utils import ns, line_attr
from typing import Set


class NotFunctionCallError(Exception):
    """Raise for false positive <call> nodes"""


def _handle_function(func_node):
    """Given a <function> node,
    return function name and function range (start & end lineno)"""
    # function name
    name_node = func_node.find('srcml:name', ns)
    func_name, start_line = _handle_function_name(name_node)
    if not func_name or not start_line:
        print('ERROR: _handle_function fails to extract name or location.')
        return None, None, None

    # function body
    block_node = func_node.find('srcml:block', ns)
    if block_node is None:
        try:
            block_node = func_node.xpath('./following-sibling::srcml:block',
                                         namespaces=ns)[0]
        except:
            print("ERROR: %s has no block_node." % func_name)
            return func_name, start_line, None
    try:
        pos_node = block_node.find('pos:position', ns)
        end_line = int(pos_node.attrib[line_attr])
    except:
        print("ERROR: %s's block_node doesn't have position info." % func_name)
        return func_name, start_line, None

    return func_name, start_line, end_line


def _handle_function_name(name_node):
    """Given an <name> node,
    return its text content and position (line)"""
    name, line = None, None
    if name_node is not None:
        if name_node.text:
            name = name_node.text
            line = int(name_node.attrib[line_attr])
        else:
            # In this case, name_node should have three children
            # assert len(name_node) == 3
            # the first children should be another name node
            # the second children is the operator "::"
            # the third children is yet another name node
            # Example: ratio_string<Ratio>::symbol
            # name_node[0] -> ratio_string<Ratio>
            # name_node[1] -> ::
            # name_node[2] -> symbol
            line = int(name_node[2].attrib[line_attr])
            name = name_node[2].text
    return name, line


def _handle_call(call_node):
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
        filename = ast.attrib['filename']
        for function in ast.findall('./srcml:function', namespaces=ns):
            caller_name, _, _ = _handle_function(function)
            if not caller_name:
                continue

            if caller_name not in ccgraph:
                ccgraph.add_node(caller_name, [filename])
            else:
                files: Set[str] = ccgraph.files(caller_name)
                if filename not in files:
                    files.add(filename)
                    ccgraph.update_node_files(caller_name, files)

            for call in function.xpath('.//srcml:call', namespaces=ns):
                try:
                    callee_name = _handle_call(call)
                except NotFunctionCallError:
                    continue
                except:
                    print("Callee name not found (in %s)" % caller_name)
                    continue

                if callee_name not in ccgraph:
                    # Pass [] to files argument since we don't know
                    # which file this node belongs to
                    ccgraph.add_node(callee_name, [])
                ccgraph.add_edge(caller_name, callee_name)

    for func, fstat in change_stats.items():
        if func not in ccgraph:
            print("%s in change_stats but not in ccgraph" % func)
            continue
        ccgraph.update_node_history(func, fstat['adds'], fstat['dels'])


def get_func_ranges_c(root):
    func_names, func_ranges = [], []
    for func_node in root.findall('./srcml:function', namespaces=ns):

        func_name, start_line, end_line = _handle_function(func_node)
        if not (func_name and start_line and end_line):
            continue

        func_ranges.append([start_line, end_line])
        func_names.append(func_name)
    return func_names, func_ranges
