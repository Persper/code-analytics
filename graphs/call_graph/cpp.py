
ns = {'srcml': 'http://www.srcML.org/srcML/src', 'pos': 'http://www.srcML.org/srcML/position'}

def get_func_ranges_cpp(root):
    func_ranges, func_names = [], []
    for func_node in root.xpath('./srcml:constructor | ./srcml:function', namespaces=ns):

        func_name, start_line, end_line = handle_function(func_node) 
        if not (func_name and start_line and end_line):
            continue

        func_ranges.append([start_line, end_line])
        func_names.append(func_name)
    return func_names, func_ranges

def handle_name(name_node):
    func_id, line = None, None
    if name_node != None:
        if name_node.text:
            func_id = name_node.text
            line = int(name_node.attrib['{http://www.srcML.org/srcML/position}line'])
        else:
            try:
                # alternative solution is to use 
                # graphs.call_graph.utils.transform_node_to_src
                class_name = name_node[0].text
                line = int(name_node[0].attrib['{http://www.srcML.org/srcML/position}line'])
                assert(name_node[1].text == "::")
                func_name = name_node[2].text
                func_id = "{}::{}".format(class_name, func_name)
            except:
                import pdb
                pdb.set_trace()
    return func_id, line

def handle_function(func_node):

    name_node = func_node.find('srcml:name', ns)
    func_id, start_line = handle_name(name_node)
    if not func_id or not start_line:
        print('Function name/start not found!')
        return None, None, None

    block_node = func_node.find('srcml:block', ns)
    try:
        pos_node = block_node.find('pos:position', ns)
        end_line = int(pos_node.attrib['{http://www.srcML.org/srcML/position}line'])
    except:
        return func_id, None, None 

    return func_id, start_line, end_line
