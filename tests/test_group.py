import supercollider

from tests.shared import server

def test_group(server):
    group1 = supercollider.Group(server)
    assert group1.id > 0
    group2 = supercollider.Group(server)
    assert group2.id == group1.id + 1
    group1.free()
    group2.free()
