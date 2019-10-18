import pytest
import supercollider

from tests.shared import SC_DUMMY_PORT, SC_REAL_PORT

@pytest.fixture(scope="module")
def server():
    server = supercollider.Server(port=SC_REAL_PORT)
    return server

def test_server_connection_fail():
    with pytest.raises(supercollider.SuperColliderConnectionError) as excinfo:
        server = supercollider.Server(port=SC_DUMMY_PORT)

def test_server_sync(server):
    rv = server.sync()
    assert rv

def test_server_get_status(server):
    rv = server.get_status()
    assert rv
    assert rv["num_ugens"] >= 0
    assert rv["num_synths"] >= 0
    assert rv["num_groups"] >= 0
    assert rv["num_synthdefs"] >= 0
    assert rv["cpu_average"] > 0
    assert rv["cpu_peak"] > 0
    assert rv["sample_rate_nominal"] > 0
    assert rv["sample_rate_actual"] > 0

def test_server_get_version(server):
    rv = server.get_version()
    print(rv)
    assert rv
    assert isinstance(rv["program_name"], str)
    assert rv["version_major"] == 3
    assert rv["version_minor"] >= 0
    assert isinstance(rv["version_patch"], str)
    assert isinstance(rv["git_branch"], str)
    assert isinstance(rv["commit_hash"], str)
