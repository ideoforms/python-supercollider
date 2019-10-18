import pytest
import supercollider

SC_DUMMY_PORT = 57999
SC_REAL_PORT = 57110

@pytest.fixture(scope="module")
def server():
    server = supercollider.Server(port=SC_REAL_PORT)
    return server
