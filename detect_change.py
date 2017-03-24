def get_intersected_length(a, b):
    """
    >>> get_intersected_length([1, 9], [2, 8])
    7
    >>> get_intersected_length([2, 8], [1, 9])
    7
    >>> get_intersected_length([1, 4], [1, 5])
    4
    >>> get_intersected_length([2, 10], [4, 11])
    7  
    """
    start = a[0] if a[0] >= b[0] else b[0]
    end = a[1] if a[1] <= b[1] else b[1]
    if start > end:
        return 0
    else:
        return end - start + 1

def get_changed_functions(func_names, func_ranges, additions, deletions):
    """func_names and func_ranges are extracted from old src file,
    so new functions are not included. 
    This function assumes func_names and func_ranges are in same order.
    Also func_ranges are sorted.
    """
    info = {}
    
    def update_info(fn, num_lines):
        if fn in info:
            info[fn] += num_lines
        else:
            info[fn] = num_lines
    
    add_ptr, del_ptr = 0, 0
    num_adds, num_dels = len(additions), len(deletions)
    for fn, fr in zip(func_names, func_ranges):
        for i in range(add_ptr, num_adds):
            if fr[0] <= additions[i][0] <= fr[1]:
                update_info(fn, additions[i][1])
                add_ptr = i + 1
    
        for j in range(del_ptr, num_dels):
            inter_length = get_intersected_length(fr, deletions[j])
            if inter_length > 0:
                update_info(fn, inter_length)
                del_ptr = j
                
    return info