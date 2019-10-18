"""
Control the SuperCollider audio synthesis server.

Example:

    from supercollider import Server, Synth
    server = Server()
    synth = Synth(server, 'sine', { 'freq' : 440.0 })
    synth.free()

"""

__author__ = "Daniel Jones <http://www.erase.net/>"
__all__ = ["Server", "Synth", "Group", "Buffer"]
__all__ += ["SuperColliderConnectionError"]
__all__ += ["ADD_AFTER", "ADD_BEFORE", "ADD_REPLACE", "ADD_TO_HEAD", "ADD_TO_TAIL"]
__all__ += ["HEADER_FORMAT_WAV", "HEADER_FORMAT_AIFF", "HEADER_FORMAT_IRCAM", "HEADER_FORMAT_NEXT", "HEADER_FORMAT_RAW"]
__all__ += ["SAMPLE_FORMAT_FLOAT", "SAMPLE_FORMAT_ALAW", "SAMPLE_FORMAT_DOUBLE", "SAMPLE_FORMAT_INT8", "SAMPLE_FORMAT_INT16", "SAMPLE_FORMAT_INT24", "SAMPLE_FORMAT_INT32", "SAMPLE_FORMAT_MULAW"]

from .server import Server
from .synth import Synth
from .group import Group
from .buffer import Buffer
from .bus import ControlBus, AudioBus
from .exceptions import SuperColliderConnectionError, SuperColliderAllocationError

from .globals import ADD_AFTER, ADD_BEFORE, ADD_REPLACE, ADD_TO_HEAD, ADD_TO_TAIL
from .globals import HEADER_FORMAT_WAV, HEADER_FORMAT_AIFF, HEADER_FORMAT_IRCAM, HEADER_FORMAT_NEXT, HEADER_FORMAT_RAW
from .globals import SAMPLE_FORMAT_FLOAT, SAMPLE_FORMAT_ALAW, SAMPLE_FORMAT_DOUBLE, SAMPLE_FORMAT_INT8, SAMPLE_FORMAT_INT16, SAMPLE_FORMAT_INT24, SAMPLE_FORMAT_INT32, SAMPLE_FORMAT_MULAW
