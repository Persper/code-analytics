from unittest.mock import patch

from persper.analytics.c import CGraphServer
from persper.analytics.cpp import CPPGraphServer
from persper.analytics.graph_server import GraphServer


def test_file_filter():
    gs = CGraphServer()
    assert gs.filter_file('io.cpp') is False
    assert gs.filter_file('random.c') is True
    assert gs.filter_file('src/random_dir/random.h') is True

    gs2 = CPPGraphServer()
    assert gs2.filter_file('io.cpp') is True
    assert gs2.filter_file('random.c') is True
    assert gs2.filter_file('src/random_dir/random.h') is True
    assert gs2.filter_file('random.js') is False


@patch.multiple(GraphServer, __abstractmethods__=set())
def test_graph_server_filter_file():
    gs = GraphServer()
    assert gs.filter_file('merico.rb') is True
    assert gs.filter_file('random.py') is True
    assert gs.filter_file('examples/example.c') is False
    gs.exclude_patterns = []
    assert gs.filter_file('examples/example.c') is True
