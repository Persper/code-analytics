def reduce_graph_history_truth(history_truth):
    reduced = {}
    for csha, history in history_truth.items():
        c = {}
        for fid, change in history.items():
            fn = fid.split(':')[2]
            if fn in c:
                c[fn] = merge_change(c[fn], change)
            else:
                c[fn] = change
        reduced[csha] = c
    return reduced


def merge_change(a, b):
    merged = {
        'adds': a['adds'] + b['adds'],
        'dels': a['dels'] + b['dels'],
    }
    return merged


def reduce_graph_edge_truth(edge_truth):
    reduced = set()
    for edge in edge_truth:
        reduced.add((edge[0].split(':')[2], edge[1].split(':')[2]))
    return reduced


def reduce_graph_file_truth(file_truth):
    reduced = {}
    for fid, files in file_truth.items():
        fn = fid.split(':')[2]
        if fn in reduced:
            reduced[fn] = reduced[fn].union(files)
        else:
            reduced[fn] = files
    return reduced
