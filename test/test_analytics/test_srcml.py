import os
import re
from persper.analytics.srcml import src_to_tree
from persper.util.path import root_path


def test_src_to_tree():
    filename = 'patch_test_files/example.cc'
    full_path = os.path.join(root_path, 'test/test_analytics', filename)
    with open(full_path, 'r') as f:
        src = f.read()
    root = src_to_tree(filename, src)
    assert bool(re.match(r'.+\.cc$', root.attrib['filename']))
    assert root.attrib['filename'] == 'patch_test_files/example.cc'
