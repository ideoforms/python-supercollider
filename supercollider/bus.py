from . import globals


class Bus (object):
    def __init__(self, server, channels):
        self.server = server
        self.channels = channels
        self.id = None

    def free(self):
        pass

class ControlBus (Bus):
    def __init__(self, server, channels):
        super(type(self), self).__init__(server, channels)
        self.id = globals.CONTROL_BUS_ALLOCATOR.allocate(channels)

    def free(self):
        globals.CONTROL_BUS_ALLOCATOR.free(self.id)

class AudioBus (Bus):
    def __init__(self, server, channels):
        super(type(self), self).__init__(server, channels)
        self.id = globals.AUDIO_BUS_ALLOCATOR.allocate(channels)

    def free(self):
        globals.AUDIO_BUS_ALLOCATOR.free(self.id)
