import pytest
from persper.analytics.graph_server import GO_FILENAME_REGEXES
from persper.analytics.go import GoGraphServer

GO_GRAPH_SERVER_PORT = 9089


@pytest.fixture(scope='module')
def gs():
    server_address = 'http://127.0.0.1:%d' % GO_GRAPH_SERVER_PORT
    return GoGraphServer(server_address, GO_FILENAME_REGEXES)


def test_analzyer_go(gs):
    assert (gs.filter_file('main.go') is True)
    assert (gs.filter_file('foo.go') is True)
    assert (gs.filter_file('lib/bar.go') is True)
    assert (gs.filter_file('./lib/bar.go') is True)

    assert (gs.filter_file('vendor/main.go') is False)
    assert (gs.filter_file('lib/vendor/main.go') is False)
    assert (gs.filter_file('./lib/vendor/foo.go') is False)
