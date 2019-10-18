import pytest
import supercollider

from tests.shared import server

def test_synth_create(server):
    synth = supercollider.Synth(server, "sine", { "freq": 440.0,  "gain": -24 })
    assert synth.id > 0
    assert synth.get("freq") == 440.0
    synth.set("freq", 880.0)
    assert synth.get("freq") == 880.0
    synth.free()
