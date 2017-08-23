import networkx as nx
from lxml import etree
from graphs.call_graph.utils import transform_node_to_src, remove_edges_of_node
from graphs.call_graph.utils import ns, line_attr


def generate_fid(class_name, func_name):
    return class_name + ':' + func_name


def decompose_fid(func_id):
    return func_id.split(':')


def get_specifiers(node):
    """Helper function to first find all specifier nodes
    and then return their texts"""
    return [n.text for n in node.findall('./srcml:specifier', ns)]


def handle_name_node(name_node):
    return transform_node_to_src(name_node).strip()

    """
    child_nodes = name_node.getchildren()
    text_of_itself = name_node.text or ''
    if len(child_nodes) == 0:
        return text_of_itself
    else:
        child_names = []
        for child_node in child_nodes:
            child_names.append(handle_name_node(child_node))
        return text_of_itself + ''.join(child_names)
    """


def get_name(node):
    """Helper function to first find name node and then parse name"""
    return handle_name_node(node.find('srcml:name', ns))


def get_type(node):
    """First get type node, then get type node's name node,
    finally returns node's type"""
    type_node = node.find('srcml:type', ns)
    return handle_name_node(type_node.find('srcml:name', ns))


def handle_decl_node(decl_node):
    type_node = decl_node.find('srcml:type', ns)
    type_name_node = type_node.find('srcml:name', ns)
    name_node = decl_node.find('srcml:name', ns)

    try:
        type_name = handle_name_node(type_name_node)
        var_name = handle_name_node(name_node)
    except:
        import pdb
        pdb.set_trace()

    return type_name, var_name


def handle_decl_stmt_node(decl_stmt_node, local_env):
    """
    Node Structure:
        A <decl_stmt> node consists of one or more <decl> nodes,
        each <decl> has a <type> node and a <name> node.
        The <type> node may or may not has a <name> node, the following
        declaration statement is an example:

            int c, char2, char3;
    """
    prev_type = None
    decl_nodes = decl_stmt_node.findall('./srcml:decl', ns)
    for decl_node in decl_nodes:
        type_node = decl_node.find('./srcml:type', ns)
        type_name_node = type_node.find('./srcml:name', ns)
        if type_name_node is None:
            type_name = prev_type
        else:
            type_name = handle_name_node(type_name_node)
        var_name = get_name(decl_node)
        local_env[var_name] = type_name
        prev_type = type_name


def handle_call_node(call_node, cl_name, local_env, env):
    """Parse a call node and return the identifer of the function being called
    Type of calls we handle:
        Case 1: doSomething(args)
            doSomething is a public/private static/instance
                member method of cl_name
        Case 2: A a = new A()
            A is a class (env), A's constructor function is called in this case
        Case 3: a.doSomething(args)
            a is an object, could be newly instantiated in this
                function (local_env),
                or could be passed as a parameter (local_env),
                or could be this class's public/private member variable (env)
            doSomething could be either a static method or a instance method
        Case 4: A.doSomething(args)
            A is a class (env)
            doSomething is one of A's static methods
        Case 5: A.var.doSomething(args)
            A is a class (env)
            var is a public static member of class A (env)
        Case 6: a.var.doSomething(args)
            a is an object, could be newly instantiated in this
                function (local_env),
                or could be passed as a parameter (local_env),
                or could be this class' public/private member variable (env)
            var is a public (static) member of object a (local_env & env)

    Returns:
        A String representing the signature of the function being called
    """
    call_name = get_name(call_node)

    names_lst = [n.strip() for n in call_name.split('.')]
    callee_func_name = names_lst[-1]
    if len(names_lst) == 1:
        previous_node = call_node.getprevious()
        if previous_node is not None and previous_node.text == 'new':
            # Case 1: calling constructor
            callee_cl_name = callee_func_name
        else:
            # Case 2: calling member method
            callee_cl_name = cl_name
        return generate_fid(callee_cl_name, callee_func_name)
    elif len(names_lst) == 2:
        niq = names_lst[0]  # niq => name in question
        # check local_env first
        if niq in local_env:
            # Case 3 (local_env)
            var_name = niq
            callee_cl_name = local_env[var_name]
            return generate_fid(callee_cl_name, callee_func_name)
        elif niq in env[cl_name]['var']:
            # case 3 (env)
            var_name = niq
            callee_cl_name = env[cl_name]['var'][var_name]['type']
            return generate_fid(callee_cl_name, callee_func_name)
        elif niq in env:
            # Case 4
            return generate_fid(niq, callee_func_name)
        else:
            # something went wrong, niq is probably a class not in env
            # print("WARNING: niq not found in both env and local_env")
            return generate_fid(niq, callee_func_name)
    else:
        # Case 5 or 6
        callee_cl_name = None
        if names_lst[0] in local_env:
            callee_cl_name = local_env[names_lst[0]]
            for n in names_lst[1:-1]:
                callee_cl_name = env[callee_cl_name]['var'][n]['type']
            return generate_fid(callee_cl_name, callee_func_name)
        elif names_lst[0] in env[cl_name]['var']:
            callee_cl_name = env[cl_name]['var'][names_lst[0]]['type']
            for n in names_lst[1:-1]:
                callee_cl_name = env[callee_cl_name]['var'][n]['type']
            return generate_fid(callee_cl_name, callee_func_name)
        elif names_lst[0] in env:
            callee_cl_name = names_lst[0]
            for n in names_lst[1:-1]:
                callee_cl_name = env[callee_cl_name]['var'][n]['type']
            return generate_fid(callee_cl_name, callee_func_name)
        else:
            # something went wrong, names_lst[0] is probably a class not in env
            # print("WARNING: names_lst[0] not found in both env and local_env")
            approx_callee_cl_name = '.'.join(names_lst[:-1])
            return generate_fid(approx_callee_cl_name, callee_func_name)


def handle_param_lst_node(param_lst_node):
    local_env = {}
    param_nodes = param_lst_node.findall('./srcml:parameter', ns)
    for param_node in param_nodes:
        decl_node = param_node.find('./srcml:decl', ns)
        type_name, var_name = handle_decl_node(decl_node)
        local_env[var_name] = type_name
    return local_env


def handle_func_node(func_node, class_name, G, new_func, fid_to_file, env):
    """
    Args:
        class_name: A String, name of the class this function belongs to
        G: A nx.DiGraph object, storing the actual call graph
        new_func: A dictionary, mapping a new function's identifer (fid)
            to its size
        fid_to_file: A dictionary, mapping fid to the file it belongs to
        env: A dictionary, storing global environment

    Workflow Summary:
        1. Parse function name and generate fid
        2. Add caller function to call graph G
        3. Initialize local_env by parsing parameter list
        4. Iterate through subnodes of this function in document order
            a. For <call> node, parse it and get callee_fid,
                add this new edge to call graph G
            b. For <decl> node, parse it and update local_env

    Node Structure:
        <function> node's direct children include <name>, <specifier>,
        <block>, <parameter_list>

    TODOs:
        1. Function Overload
            a. Primitive type
        2. Polymorphism
        3. Collection
        4. Array
        5. Add logic to remove variable from local_env
        6. Nested class
        7. Anonymous class
    """
    name_node = func_node.find('./srcml:name', ns)
    block_node = func_node.find('./srcml:block', ns)
    block_pos_node = block_node.find('./pos:position', ns)
    if block_pos_node is None:
        # probably a srcML parsing error
        return
    param_lst_node = func_node.find('./srcml:parameter_list', ns)

    func_name = get_name(func_node)
    caller_fid = generate_fid(class_name, func_name)
    start_line = int(name_node.attrib[line_attr])
    end_line = int(block_pos_node.attrib[line_attr])
    num_lines = end_line - start_line + 1

    # local_env maps variable name to class name
    try:
        local_env = handle_param_lst_node(param_lst_node)
    except:
        print("Failed to parse parameter list for %s" % caller_fid)
        return

    if caller_fid not in G:
        # Case 1: hasn't been defined and hasn't been called
        new_func[caller_fid] = num_lines
        G.add_node(caller_fid, {'num_lines': num_lines, 'defined': True})
    elif not G.node[caller_fid]['defined']:
        # Case 2: has been called but hasn't been defined
        new_func[caller_fid] = num_lines
        G.node[caller_fid]['defined'] = True
        G.node[caller_fid]['num_lines'] = num_lines
    else:
        # Case 3: has been called and has been defined
        # it is modified in the latest commit
        # no need to add it to new_func or
        # update G.node[caller_fid]['num_lines']
        pass

    fid_to_file[caller_fid] = env[class_name]['filename']

    for node in block_node.iter('{*}call', '{*}decl_stmt'):
        if 'call' in node.tag:
            try:
                callee_fid = handle_call_node(node, class_name, local_env, env)
            except:
                print("Excpetion in handle_call_node.")
                continue
            if callee_fid not in G:
                G.add_node(callee_fid, {'num_lines': 1, 'defined': False})
            G.add_edge(caller_fid, callee_fid)
        else:
            handle_decl_stmt_node(node, local_env)


def handle_class_node(class_node, G, new_func, fid_to_file, env):
    class_name = get_name(class_node)

    block_node = class_node.find('./srcml:block', ns)
    func_nodes = block_node.findall('./srcml:function', ns)
    for func_node in func_nodes:
        handle_func_node(func_node, class_name, G, new_func, fid_to_file, env)


def prepare_env_class(class_node, env):
    """
    Official Access Level Tutorial:
        https://docs.oracle.com/javase/tutorial/java/javaOO/accesscontrol.html

    Node Structure:
        <super> node can have <extends> node or <implements> node
            as its direct child

    Assumptions and TODOs:
        1. We assume every class method has modifiers (package private is rare)
        2. We currently don't distinguish between `protected` and `public`
        3. We don't keep record of methods' return types and arguments' types
    """
    class_name = get_name(class_node)
    filename = class_node.getparent().attrib['filename']
    # Class members are made of 2 things:
    #   1. class's variable
    #   2. class's methods
    cl_env = {'var': {}, 'method': {}, 'filename': filename}
    env[class_name] = cl_env

    # `this` and `super`
    cl_env['var']['this'] = {'is_public': False,
                             'is_static': False,
                             'type': class_name}
    super_node = class_node.find('./srcml:super', ns)
    if super_node is not None:
        extends_node = super_node.find('./srcml:extends', ns)
        if extends_node is not None:
            super_cl_name = get_name(extends_node)
            cl_env['var']['super'] = {'is_public': False,
                                      'is_static': True,
                                      'type': super_cl_name}

    block_node = class_node.find('./srcml:block', ns)

    # member variables
    decl_stmt_nodes = block_node.findall('./srcml:decl_stmt', ns)
    for decl_stmt_node in decl_stmt_nodes:
        decl_node = decl_stmt_node.find('./srcml:decl', ns)
        var_name = get_name(decl_node)
        var_type = get_type(decl_node)
        specifiers = get_specifiers(decl_node)
        is_public = 'protected' in specifiers or 'public' in specifiers
        is_static = 'static' in specifiers
        cl_env['var'][var_name] = {'is_public': is_public,
                                   'is_static': is_static,
                                   'type': var_type}

    # member methods
    func_nodes = block_node.findall('./srcml:function', ns)
    for func_node in func_nodes:
        func_name = get_name(func_node)
        specifiers = get_specifiers(func_node)
        is_public = 'protected' in specifiers or 'public' in specifiers
        is_static = 'static' in specifiers
        cl_env['method'][func_name] = {'is_public': is_public,
                                       'is_static': is_static}


def prepare_env(root, env=None):
    """
    env: class_name => [var/method] => [var_name/method_name]
    """
    if env is None:
        env = {}

    class_nodes = root.findall('./srcml:class', ns)
    for class_node in class_nodes:
        prepare_env_class(class_node, env)
    return env


def build_call_graph_java(roots, G=None, env=None):
    if G is None:
        G = nx.DiGraph()

    new_func = {}
    fid_to_file = {}

    # Initialize global environment
    for root in roots:
        env = prepare_env(root, env=env)

    # Build call graph
    for root in roots:
        class_nodes = root.xpath('./srcml:class', namespaces=ns)
        for class_node in class_nodes:
            handle_class_node(class_node, G, new_func, fid_to_file, env)
    return G, new_func, fid_to_file, env


def update_call_graph_java(G, roots, modified_func, env=None):
    for fid in modified_func:
        if fid in G:
            remove_edges_of_node(G, fid, in_edges=False)
            G.node[fid]['num_lines'] += modified_func[fid]

    # here roots should be constructed from the more recent commit
    # new functions and their sizes are stored in new_func dictionary
    _, new_func, _, _ = build_call_graph_java(roots, G, env=env)
    return new_func


def get_func_ranges_java(root):
    fids, func_ranges = [], []
    for class_node in root.xpath('.//srcml:class', namespaces=ns):
        try:
            class_name = get_name(class_node)
        except:
            print("Class doesn't have name.")
            continue

        block_node = class_node.find('./srcml:block', ns)
        for func_node in block_node.findall('./srcml:function', ns):
            try:
                func_name = get_name(func_node)
                fid = generate_fid(class_name, func_name)

                name_node = func_node.find('./srcml:name', ns)
                block_node = func_node.find('./srcml:block', ns)
                block_pos_node = block_node.find('./pos:position', ns)
                start_line = int(name_node.attrib[line_attr])
                end_line = int(block_pos_node.attrib[line_attr])
            except:
                continue

            fids.append(fid)
            func_ranges.append([start_line, end_line])
    return fids, func_ranges
