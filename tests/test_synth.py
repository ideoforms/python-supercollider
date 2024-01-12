import pytest
import supercollider
from threading import Event

from tests.shared import server

def test_synth_create(server):
    synth = supercollider.Synth(server, "sine", {"freq": 440.0, "gain": -24})
    assert synth.id > 0
    synth.free()

def test_synth_get_set(server):
    synth = supercollider.Synth(server, "sine", {"freq": 440.0, "gain": -24})
    assert synth.get("freq") == 440.0
    synth.set("freq", 880.0)
    assert synth.get("freq") == 880.0
    synth.free()

def test_synth_get_nonblocking(server):
    synth = supercollider.Synth(server, "sine", {"freq": 440.0, "gain": -24})

    rv = None
    event = Event()
    def callback(args):
        nonlocal rv
        rv = args
        event.set()

    synth.get("freq", callback=callback, blocking=False)
    event.wait(1.0)
    assert rv == 440.0
    synth.free()

def test_synth_actions(server):
    group = supercollider.Group(server)

    synth0 = supercollider.Synth(server, "sine", {"gain": -96}, target=group)
    tree = server.query_tree(group)
    assert tree[2] == 1
    assert tree[3] == synth0.id

    synth1 = supercollider.Synth(server, "sine", {"gain": -96}, target=group, action=supercollider.ADD_TO_HEAD)
    tree = server.query_tree(group)
    assert tree[2] == 2
    assert tree[3] == synth1.id

    synth2 = supercollider.Synth(server, "sine", {"gain": -96}, target=group, action=supercollider.ADD_TO_TAIL)
    tree = server.query_tree(group)
    print(tree)
    assert tree[2] == 3
    assert tree[3] == synth1.id
    assert tree[9] == synth2.id

    synth3 = supercollider.Synth(server, "sine", {"gain": -96}, target=synth1, action=supercollider.ADD_AFTER)
    tree = server.query_tree(group)
    print(tree)
    assert tree[2] == 4
    assert tree[3] == synth3.id

    synth4 = supercollider.Synth(server, "sine", {"gain": -96}, target=synth1, action=supercollider.ADD_BEFORE)
    tree = server.query_tree(group)
    print(tree)
    assert tree[2] == 5
    assert tree[9] == synth4.id

    group.free()
