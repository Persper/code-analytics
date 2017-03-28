import re
import os.path
import subprocess
from git import Repo
import networkx as nx

from graphs.write_graph_to_dot import write_G_to_dot_with_pr

def underscore_to_camelcase(value):
    def camelcase(): 
        while True:
            yield str.capitalize

    c = camelcase()
    return "".join(next(c)(x) if x else '_' for x in value.split("_"))

def get_func_ranges_ruby(src, fname):
    
    def get_prefix(fname):
        return fname
    
    fname = os.path.basename(fname).split('.')[0]
    prefix = underscore_to_camelcase(get_prefix(fname))
        
    re_def = re.compile("^\s*def\s+(?P<class_method>self\.)?(?P<func_name>\w+\??)\s*\(?.*\)?$")
    func_ids = []
    func_ranges = []
    ptr = -1
    num_lines = 0
    for lineno, line in enumerate(src.split('\n'), 1):
        num_lines += 1
        m = re_def.search(line)
        if m:
            d = m.groupdict()
            if d['class_method'] or fname.endswith('_helper.rb'):
                op = "::"
            else:
                op = "#"
            func_ids.append(prefix + op + d['func_name'])
            
            if ptr != -1:
                func_ranges.append([ptr, lineno - 1])
            ptr = lineno
    if ptr != -1:
        func_ranges.append([ptr, num_lines])
        
    return func_ids, func_ranges

    
def fname_filter_ruby(fname):
    return fname.endswith('.rb')

