import pytest
from persper.analytics.graph_server import GO_FILENAME_REGEXES
from persper.analytics.go import GoGraphServer


@pytest.fixture(scope='module')
def gs():
    return GoGraphServer(None, GO_FILENAME_REGEXES)


def test_analzyer_go(gs):
    assert (gs.filter_file('main.go') is True)
    assert (gs.filter_file('foo.go') is True)
    assert (gs.filter_file('lib/bar.go') is True)
    assert (gs.filter_file('./lib/bar.go') is True)

    assert (gs.filter_file('vendor/main.go') is False)
    assert (gs.filter_file('lib/vendor/main.go') is False)
    assert (gs.filter_file('./lib/vendor/foo.go') is False)
