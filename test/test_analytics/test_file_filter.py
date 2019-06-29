
from persper.analytics.c import CGraphServer
from persper.analytics.cpp import CPPGraphServer


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
