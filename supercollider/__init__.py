"""
Control the SuperCollider audio synthesis server.

Example:

    from supercollider import Server, Synth
    server = Server()
    synth = Synth(server, 'sine', { 'freq' : 440.0 })
    synth.free()

"""

__author__ = "Daniel Jones <http://www.erase.net/>"
__all__ = ["Server", "Synth", "Group"]
__all__ += ["ADD_AFTER", "ADD_BEFORE", "ADD_REPLACE", "ADD_TO_HEAD", "ADD_TO_TAIL"]

from .server import Server
from .synth import Synth
from .group import Group

from .globals import ADD_AFTER, ADD_BEFORE, ADD_REPLACE, ADD_TO_HEAD, ADD_TO_TAIL