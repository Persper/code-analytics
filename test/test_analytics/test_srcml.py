import os
from persper.analytics.srcml import src_to_tree
from persper.util.path import root_path


def test_src_to_tree():
    filename = 'example.cc'
    full_path = os.path.join(root_path, 'test/test_analytics', filename)
    with open(full_path, 'r') as f:
        src = f.read()
    root = src_to_tree(filename, src)
    assert(root.attrib['filename'] == filename)
