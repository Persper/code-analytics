import networkx as nx

ns = {'srcml': 'http://www.srcML.org/srcML/src', 'pos': 'http://www.srcML.org/srcML/position'}

class NotFunctionCallError(Exception):
    """Raise for false positive <call> nodes"""

def handle_function(func_node):
    """Given a <function> node, 
    return function name and function range (start & end lineno)"""
    
    name_node = func_node.find('srcml:name', ns)
    func_name, start_line = handle_name(name_node)
    if not func_name or not start_line:
        print('Function name/start not found!') # very unlikely to happen
        return None, None, None
    
    block_node = func_node.find('srcml:block', ns)
    if block_node == None:
        try:
            block_node = func_node.xpath('./following-sibling::srcml:block', namespaces=ns)[0]
        except:
            print("More edge cases for block node! (in function {})".format(func_name))
            return func_name, None, None
    try:
        pos_node = block_node.find('pos:position', ns)
        end_line = int(pos_node.attrib['{http://www.srcML.org/srcML/position}line'])
    except:
        print("Block node doesn't have position node inside!")
        return func_name, None, None
    
    return func_name, start_line, end_line

def handle_name(name_node):
    """Given an <name> node, 
    return its text content and position (line)"""
    text, line = None, None
    if name_node != None:
        text = name_node.text
        line = int(name_node.attrib['{http://www.srcML.org/srcML/position}line'])
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
    if name_node == None:
        # Case 1
        raise NotFunctionCallError()
    callee_name = name_node.text
    if callee_name == None:
        # Case 2
        callee_name = name_node[-1].text
    return callee_name

def remove_edges_of_node(G, n):
    """Remove all edges of n, but keep the node itself in the graph
    
    >>> G3 = nx.DiGraph()
    >>> G3.add_path([0, 1, 2, 3, 4])
    >>> remove_edges_of_node(G3, 2)
    >>> G3.nodes()
    [0, 1, 2, 3, 4]
    >>> G3.edges()
    [(0, 1), (3, 4)]
    
    """
    try:
        nbrs = G.succ[n]
    except KeyError: # NetworkXError if not in self
        # raise NetworkXError("The node %s is not in the digraph."%(n, ))
        print("The node %s is not in the digraph."%(n, ))
        return 
    for u in nbrs:
        del G.pred[u][n]
    G.succ[n] = {}
    for u in G.pred[n]:
        del G.succ[u][n]
    G.pred[n] = {}
    
def get_func_ranges_c(root):
    func_ranges, func_names = [], []
    for func_node in root.findall('./srcml:function', namespaces=ns):
        
        func_name, start_line, end_line = handle_function(func_node)
        if not (func_name and start_line and end_line):
            continue
        
        func_ranges.append([start_line, end_line])
        func_names.append(func_name)
    return func_names, func_ranges
    
def update_call_graph(roots, change_info, G):
    for func_name in change_info:
        if func_name in G:
            remove_edges_of_node(G, func_name)
            G.node[func_name]['num_lines'] += change_info[func_name]
        
    # here roots should be constructed from new commit
    # info of new functions is added to change_info
    build_call_graph(roots, change_info, G)
        

def build_call_graph(roots, change_info, G=None):
    if G == None:
        G = nx.DiGraph()
        
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
                change_info[caller_name] = num_lines
                G.add_node(caller_name, {'num_lines': num_lines, 'defined': True}) 
            elif not G.node[caller_name]['defined']:
                # Case 2: has been called but hasn't been defined
                change_info[caller_name] = num_lines
                G.node[caller_name]['defined'] = True
                G.node[caller_name]['num_lines'] = num_lines
            else:
                # Case 3: has been called and has been defined
                # pass because its change_info[caller_name] and 
                # G.node[caller_name]['num_lines'] have already been updated
                pass
                
                
            func_to_file[caller_name] = root.attrib['filename']
            
            # handle all function calls
            for call_node in func_node.xpath('.//srcml:call', namespaces=ns):
                
                try:
                    callee_name = handle_call(call_node)
                except NotFunctionCallError:
                    continue
                except:
                    print("Callee name not found! (in function {})".format(caller_name))
                    continue
                
                if callee_name not in G:
                    G.add_node(callee_name, {'num_lines': 1, 'defined': False})
                G.add_edge(caller_name, callee_name)
                
    return G, func_to_file
