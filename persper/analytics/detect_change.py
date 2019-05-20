import re

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

def get_add_line_number(additions, deletions):
    """
    Get the line number in new src for each added block
    Input:
        additions = [[7, 31], [27, 3], [44, 1], [50, 2], [70, 1], [77, 2], [99, 2]]
        deletions = [[32, 44], [56, 70]]
    Output:
        [[8, 38], [59, 61], [66, 66], [73, 74], [80, 80], [88, 89], [112, 113]]
        ground truth:
        https://github.com/basicthinker/Sexain-MemController/commit/f050c6f6dd4b1d3626574b0d23bb41125f7b75ca
    """
    add_line_number = []
    del_ptr, num_dels = 0, len(deletions)
    add_num, del_num = 0, 0
    for add_range in additions:
        while del_ptr < num_dels and deletions[del_ptr][1] <= add_range[0]:
            del_num += deletions[del_ptr][1] - deletions[del_ptr][0] + 1
            del_ptr += 1
        start_line = add_range[0]+1+add_num-del_num
        tmp_line_number = [start_line, start_line+add_range[1]-1]
        add_line_number.append(tmp_line_number)
        add_num += add_range[1]
    return add_line_number
#need test
def get_units(src_list, line_number_range):
    """
    Get the sum of units for each line in line_number_range
    """
    units_sum = 0
    p = re.compile(r'\w+')
    for i in range(line_number_range[0]-1, line_number_range[1]):
        if i >= len(src_list):
            break
        units_sum += len(p.findall(src_list[i]))
    return units_sum

def get_changed_functions(func_names, func_ranges, additions, deletions,
                          old_src, new_src, separate=False):
    """
    Args:
        func_names: A list of function names,
            usually extracted from old src file,
            so new functions aren't included.
        func_ranges: A sorted list of function ranges
            in the same order of func_names.
        additions: A list of pair of integers,
        deletions: A list of pair of integers,
        separate: A boolean flag, if set to True, additions and deletions are
            reported separately.

    Returns:
        A dictionary where keys are function names and values are
        number of lines edited.
    """
    info = {}

    if (func_names is None or func_ranges is None or
       additions is None or deletions is None or
       old_src is None or new_src is None):
        return info

    def update_info(fn, num_lines, num_units, key1, key2):
        """key should be one of 'adds' or 'dels'."""
        if fn in info:
            info[fn][key1] += num_lines
            info[fn][key2] += num_units
        else:
            info[fn] = {'adds': 0, 'dels': 0, 'added_units': 0, 'removed_units': 0}
            info[fn][key1] = num_lines
            info[fn][key2] = num_units

    old_src_list = old_src.split('\n')
    new_src_list = new_src.split('\n')

    add_line_number = get_add_line_number(additions, deletions)
    add_ptr, del_ptr = 0, 0
    num_adds, num_dels = len(additions), len(deletions)
    for fn, fr in zip(func_names, func_ranges):
        for i in range(add_ptr, num_adds):
            if fr[0] <= additions[i][0] < fr[1]:
                units = get_units(new_src_list, add_line_number[i])
                update_info(fn, additions[i][1], units, 'adds', 'added_units')
                add_ptr = i + 1

        for j in range(del_ptr, num_dels):
            inter_length = get_intersected_length(fr, deletions[j])
            if inter_length > 0:
                units = get_units(old_src_list, [max(fr[0],deletions[j][0]), min(fr[1],deletions[j][1])])
                update_info(fn, inter_length, units, 'dels', 'removed_units')
                del_ptr = j

    if not separate:
        for fn in info:
            info[fn] = info[fn]['adds'] + info[fn]['dels']

    return info
