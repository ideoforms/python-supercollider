from . import globals
from .exceptions import SuperColliderAllocationError

class Allocator (object):
    def __init__(self, resource_name="generic"):
        self.index = globals.ALLOCATOR_BUS_START_INDEX
        self.resource_name = resource_name
        self.capacity = globals.ALLOCATOR_BUS_CAPACITY

    def allocate(self, channels):
        if self.index <= globals.ALLOCATOR_BUS_START_INDEX + self.capacity - channels:
            rv = self.index
            self.index += channels
            return rv
        else:
            raise SuperColliderAllocationError("No more %s resources available" % self.resource_name)

    def free(self, index):
        # TODO: Implement me
        pass
