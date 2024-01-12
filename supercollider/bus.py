from __future__ import annotations
from . import globals
from typing import TYPE_CHECKING

if TYPE_CHECKING:
    from .server import Server

class Bus:
    def __init__(self, server: Server, channels: int):
        self.server = server
        self.channels = channels
        self.id = None

    def free(self):
        pass

class ControlBus(Bus):
    def __init__(self, server, channels):
        super(type(self), self).__init__(server, channels)
        self.id = globals.CONTROL_BUS_ALLOCATOR.allocate(channels)

    def free(self):
        globals.CONTROL_BUS_ALLOCATOR.free(self.id)

class AudioBus(Bus):
    def __init__(self, server, channels):
        super(type(self), self).__init__(server, channels)
        self.id = globals.AUDIO_BUS_ALLOCATOR.allocate(channels)

    def free(self):
        globals.AUDIO_BUS_ALLOCATOR.free(self.id)
