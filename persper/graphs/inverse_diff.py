
def inverse_diff(adds, dels):
    """
    >>> adds = [[11, 1], [32, 1]]
    >>> dels = [[11, 11], [31, 32]]
    >>> _inverse_diff_result(adds, dels)
    ([[10, 1], [30, 2]], [[11, 11], [31, 31]])
    """
    diff = 0
    add_ptr, del_ptr = 0, 0
    num_adds, num_dels = len(adds), len(dels)
    inv_adds, inv_dels = [], []

    def _handle_a(a):
        nonlocal diff
        inv_dels.append([diff + a[0] + 1, diff + a[0] + a[1]])
        diff += a[1]

    def _handle_d(d):
        nonlocal diff
        inv_adds.append([diff + d[0] - 1, d[1] - d[0] + 1])
        diff -= (d[1] - d[0] + 1)

    while add_ptr < num_adds or del_ptr < num_dels:
        if add_ptr < num_adds and del_ptr < num_dels:
            if adds[add_ptr][0] < dels[del_ptr][0]:
                _handle_a(adds[add_ptr])
                add_ptr += 1
            else:
                _handle_d(dels[del_ptr])
                del_ptr += 1
        elif add_ptr < num_adds and del_ptr >= num_dels:
            # we have finished dels
            _handle_a(adds[add_ptr])
            add_ptr += 1
        else:
            # we have finished adds
            _handle_d(dels[del_ptr])
            del_ptr += 1

    return inv_adds, inv_dels
