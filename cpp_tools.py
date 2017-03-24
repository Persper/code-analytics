import re
import subprocess
from git import Repo
import networkx as nx

from write_graph_to_dot import write_G_to_dot_with_pr

def get_func_ranges_cpp(src, fname):
    re_signature = re.compile("""^(?P<return_type>\w+(\s*[\*\&])?)\s+
                                ((?P<class_name>\w+)::)?
                                (?P<func_name>\w+)\s*
                                \([^;]+$
                            """, re.VERBOSE )
    func_ids = []
    func_ranges = []
    ptr = -1
    num_lines = 0
    for lineno, line in enumerate(src.split('\n'), 1):
        num_lines += 1
        m = re_signature.search(line)
        if m:
            d = m.groupdict()
            if d['class_name']:
                func_ids.append('{}::{}'.format(d['class_name'], d['func_name']))
            else:
                func_ids.append(d['func_name'])
            if ptr != -1:
                func_ranges.append([ptr, lineno - 1])
            ptr = lineno
    if ptr != -1:
        func_ranges.append([ptr, num_lines])
        
    return func_ids, func_ranges

def fname_filter_cpp(fname):
    return fname.endswith('.cc') or fname.endswith('.cpp')


