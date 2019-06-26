
from persper.analytics.c import CGraphServer
from persper.analytics.cpp import CPPGraphServer


def test_file_filter():
    gs = CGraphServer()
    assert gs.filter_file('io.cpp') == False
    assert gs.filter_file('random.c') == True
    assert gs.filter_file('src/random_dir/random.h') == True

    gs2 = CPPGraphServer()
    assert gs2.filter_file('io.cpp') == True
    assert gs2.filter_file('random.c') == True
    assert gs2.filter_file('src/random_dir/random.h') == True
    assert gs2.filter_file('random.js') == False
