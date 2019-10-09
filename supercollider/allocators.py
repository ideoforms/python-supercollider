from . import globals


class AllocatorException (Exception):
    pass


class Allocator (object):
    def __init__(self, resource_name="generic"):
        self.index = globals.ALLOCATOR_BUS_START_INDEX
        self.resource_name = resource_name
        self.capacity = globals.ALLOCATOR_BUS_CAPACITY

    def allocate(self, channels):
        if self.index <= self.capacity - channels:
            rv = self.index
            self.index += channels
            return rv
        else:
            raise AllocatorException("No more %s resources available" % self.resource_name)

    def free(self, index):
        # TODO: Implement me
        pass