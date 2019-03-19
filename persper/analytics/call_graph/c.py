from persper.analytics.call_graph.utils import ns, line_attr
from typing import Set
from persper.analytics.error import UnexpectedASTError


class UnexpectedNameNodeError(UnexpectedASTError):
    """Raise for unexpected function name node"""
    pass


class UnexpectedFunctionNodeError(UnexpectedASTError):
    """Raise when failed to parse a function's name or range"""
    pass


class NotFunctionCallError(UnexpectedASTError):
    """Raise for false positive <call> nodes"""
    pass


def _handle_function(func_node):
    """Extract name and range from a <function> node

    Args:
        func_node: an ast node with tag function

    Returns:
        tuple: function's name (str),
            start line number (int), and end line number (int)

    Raises:
        UnexpectedFunctionNodeError

    """
    # name
    name_node = func_node.find('srcml:name', ns)
    try:
        func_name, start_line = _handle_function_name(name_node)
    except UnexpectedASTError as e:
        print(type(e).__name__, e.args)
        raise UnexpectedFunctionNodeError('Failed to parse name node')

    # function body
    block_node = func_node.find('srcml:block', ns)
    if block_node is None:
        try:
            block_node = func_node.xpath('./following-sibling::srcml:block', namespaces=ns)[0]
        except IndexError:
            raise UnexpectedFunctionNodeError("%s doens't have block node" % func_name)

    try:
        pos_node = block_node.find('pos:position', ns)
        end_line = int(pos_node.attrib[line_attr])
    except AttributeError:
        raise UnexpectedFunctionNodeError("%s's block_node doesn't have position info" % func_name)

    return func_name, start_line, end_line


def _handle_function_name(name_node):
    """Extract a function's name and position from its <name> node
    Args:
        name_node: an ast node of type <name>

    Returns:
        name: A string, this function's name
        line: An int, the line number of the name node

    Raises:
        UnexpectedASTError
    """
    if name_node is None:
        raise UnexpectedNameNodeError("The function's name_node is None")
    else:
        if name_node.text:
            name = name_node.text
            line = int(name_node.attrib[line_attr])
        elif len(name_node) in [3, 5]:
            """
            Examples:

            Case 1: ratio_string<Ratio>::symbol
                name_node[0] -> ratio_string<Ratio>
                name_node[1] -> ::
                name_node[2] -> symbol

            Case 2: MemoryBase::ReverseData<1>
                name_node[0] -> MemoryBase
                name_node[1] -> ::
                name_node[2] -> ReverseData<1>
                  name_node[2][0] -> ReverseData
                  name_node[2][1] -> <1>

            Case 3: wxDateTime::Tm::IsValid
                name_node[0] -> wxDateTime
                name_node[1] -> ::
                name_node[2] -> Tm
                name_node[3] -> ::
                name_node[4] -> IsValid
            """
            line_str = name_node[-1].attrib.get(line_attr, None)
            if line_str is None:
                try:
                    line = int(name_node[-1][0].attrib[line_attr])
                except KeyError:
                    raise UnexpectedNameNodeError("No line attribute found")
                name = name_node[-1][0].text
            else:
                line = int(line_str)
                name = name_node[-1].text
        else:
            raise UnexpectedNameNodeError("Incorrect len(name_node): not in [3, 5]")
    return name, line


def _handle_call(call_node):
    """Given an <call> node, return function name being called

    Case 1: casting function pointer is not function call
        Example: tmp.sa_handler = (void (*)(int)) handler;

    Case 2: function call from struct variable
        Example: tty->write(tty)

    Raises:
        NotFunctionCallError
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


def update_graph(ccgraph, ast_list, change_stats, new_fname_to_old_fname):
    for ast in ast_list:
        filename = ast.attrib['filename']
        for function in ast.findall('./srcml:function', namespaces=ns):
            try:
                caller_name, _, _ = _handle_function(function)
            except UnexpectedFunctionNodeError as e:
                print(type(e).__name__, e.args)
                continue

            if caller_name not in ccgraph:
                ccgraph.add_node(caller_name, [filename])
            else:
                files: Set[str] = ccgraph.files(caller_name)
                old_filename = new_fname_to_old_fname.get(filename, None)
                # Case: rename
                if old_filename:
                    files.add(filename)
                    old_fname = new_fname_to_old_fname[filename]
                    if old_fname in files:
                        files.remove(old_fname)
                    ccgraph.update_node_files(caller_name, files)
                # Case: new file
                elif filename not in files:
                    files.add(filename)
                    ccgraph.update_node_files(caller_name, files)

            for call in function.xpath('.//srcml:call', namespaces=ns):
                try:
                    callee_name = _handle_call(call)
                except NotFunctionCallError as e:
                    # do not print error since we expect this to happen a lot
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

        try:
            func_name, start_line, end_line = _handle_function(func_node)
        except UnexpectedFunctionNodeError as e:
            print(type(e).__name__, e.args)
            continue

        func_ranges.append([start_line, end_line])
        func_names.append(func_name)
    return func_names, func_ranges
