import pytest
import supercollider
from supercollider.globals import ALLOCATOR_BUS_START_INDEX, ALLOCATOR_BUS_CAPACITY

from tests.shared import server

def test_bus(server):
    for cls in [supercollider.AudioBus, supercollider.ControlBus]:
        bus1 = cls(server, 2)
        assert bus1.id == ALLOCATOR_BUS_START_INDEX
        bus2 = cls(server, 2)
        assert bus2.id == ALLOCATOR_BUS_START_INDEX + 2
        remaining_channel_count = ALLOCATOR_BUS_CAPACITY - 4
        bus3 = cls(server, remaining_channel_count)
        assert bus3.id == ALLOCATOR_BUS_START_INDEX + 4
        with pytest.raises(supercollider.SuperColliderAllocationError) as excinfo:
            bus4 = cls(server, 2)
        bus1.free()
        bus2.free()
        bus3.free()
