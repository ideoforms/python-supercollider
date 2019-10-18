import pytest
import supercollider
from supercollider.globals  import ALLOCATOR_BUS_START_INDEX, ALLOCATOR_BUS_CAPACITY

from tests.shared import server

def test_bus(server):
    bus1 = supercollider.ControlBus(server, 2)
    assert bus1.id == ALLOCATOR_BUS_START_INDEX
    bus2 = supercollider.ControlBus(server, 2)
    assert bus2.id == ALLOCATOR_BUS_START_INDEX + 2
    remaining_channel_count = ALLOCATOR_BUS_CAPACITY - 4
    bus3 = supercollider.ControlBus(server, remaining_channel_count)
    assert bus3.id == ALLOCATOR_BUS_START_INDEX + 4
    with pytest.raises(supercollider.SuperColliderAllocationError) as excinfo:
        bus4 = supercollider.ControlBus(server, 2)
    bus1.free()
    bus2.free()
    bus3.free()
