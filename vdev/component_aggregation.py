import json

def set_dict(adict, *para):
    cur_dict = adict
    alen = len(para)
    if alen < 2:
        raise Exception("set_dict len(para) < 2")
    for i in range(alen):
        item = para[i]
        try:
            if i == alen - 2:
                value = para[i + 1]
                cur_dict[item] = value
                return value

            if item in cur_dict:
                cur_dict = cur_dict[item]
            else:
                sub_dict = {}
                cur_dict[item] = sub_dict
                cur_dict = sub_dict
        except:
            return None


#note: "\t<v>\t" => value field, add "\t" to be different from words in path.
VALUE_TAG = "\t<v>\t"

def build_tree_from_path_map(input_json):
    tree_map = {}
    for path in input_json:
        value = input_json[path]
        part_list = path.split("/")
        
        part_list.append(VALUE_TAG)
        part_list.append(value)
        set_dict(tree_map, *tuple(part_list))
    return tree_map


"""
fill the inner nodes with key(VALUE_TAG) and value(sum of each node's leaves' value)
"""
def fill_value_of_node(tree_map):
    if VALUE_TAG in tree_map:
        return tree_map[VALUE_TAG]
    node_value = 0
    for key in tree_map:
        node_value += fill_value_of_node(tree_map[key])
    tree_map[VALUE_TAG] = node_value
    return node_value

    
def collect_deep_and_big_target_nodes(tree_map, node_path, value_threshold):
    node_info_list = []
    b_found_value_above_threshold = False
    other_value = 0
    for key in tree_map:
        if key == VALUE_TAG:
            continue
        else:
            node_info_list_tmp, b_found_value_above_threshold_tmp = collect_deep_and_big_target_nodes(tree_map[key], node_path + "/" + key, value_threshold)
            
            if b_found_value_above_threshold_tmp:
                b_found_value_above_threshold = True
                node_info_list += node_info_list_tmp
            else:
                # if value above threshold not found,node_info_list_tmp is a list with a single aggregated result, so node_info_list_tmp.length = 1, node_info_list_tmp[0][0] is the aggregated value
                other_value += node_info_list_tmp[0][0] 
            
    if b_found_value_above_threshold:
        if other_value > 0:
            node_info_list.append( (other_value, node_path + "/...",) )
        return node_info_list, b_found_value_above_threshold
        
    value = tree_map[VALUE_TAG]
    if node_path != ".": #not root
        return [ (value, node_path,) ], value >= value_threshold
    else:#root return the first level paths
        return [ (other_value, "...",) ], value >= value_threshold


"""
example for param input_json:
{"ui.cpp": 0.0020550522811051543,
 "src/wallet/db.cpp": 0.000353362786252958,
 "db.cpp": 0.0002973690284124494,
 "src/qt/bitcoinamountfield.cpp": 0.0008160633028374406,
 "src/bloom.cpp": 0.005302888608454529,
 "src/qt/qvalidatedlineedit.cpp": 0.0006206876909743259,
 "src/qt/receivecoinsdialog.cpp": 0.00043134471221693295,
 ...
 }

example for return value:
{
"src/qt": 0.05,
"src/test/demo": 0.03,
...

}
"""
def get_aggregated_modules(original_modules, value_threshold=0.001):
    assert value_threshold > 0
    
    tree_map = build_tree_from_path_map(original_modules)
    fill_value_of_node(tree_map)
    target_node_list, flag = collect_deep_and_big_target_nodes(tree_map, ".", value_threshold)
    
    target_node_dict = {}
    for value, path in target_node_list:
        if path.startswith("./"):
            path = path[2:] #del the prefix "./" 
        target_node_dict[path] = value

    return target_node_dict


# if __name__ == '__main__':
#     output_dict = get_target_nodes_from_json(input_json, 0.001)
